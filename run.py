from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime
import plotly.graph_objects as go

app = Flask(__name__)

# Função para conectar ao banco de dados
def conectar_banco():
    return sqlite3.connect("investimentos.db")

# Página inicial
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Captura os dados do formulário
            objetivo = request.form['objetivo']
            valor_inicial = float(request.form['valor_inicial'])
            valor_mensal = float(request.form['valor_mensal'])
            tempo = int(request.form['tempo'])  # Tempo em meses
        except KeyError as e:
            return f"Erro ao receber o campo {e.args[0]}.", 400
        except ValueError:
            return "Os valores fornecidos não são válidos. Por favor, insira números.", 400

        # Calcula o rendimento com base nos dados fornecidos
        resultado, tipo_investimento = calcular_rendimento_personalizado(objetivo, valor_inicial, valor_mensal, tempo)
        

        # Data de envio e resgate
        data_envio = datetime.datetime.now()
        data_resgate = data_envio + datetime.timedelta(days=tempo * 30)

        # Salva os dados no banco de dados
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO investimentos (tipo, valor_inicial, valor_mensal, tempo, resultado, data_envio, data_resgate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (objetivo, valor_inicial, valor_mensal, tempo, resultado, data_envio, data_resgate))
            conn.commit()

        # Redireciona para a página de simulação
        return redirect(url_for(
            'simulacao',
            objetivo=objetivo,
            valor_inicial=valor_inicial,
            valor_mensal=valor_mensal,
            tempo=tempo,
            resultado=resultado,
            tipo_investimento=tipo_investimento,
            data_envio=data_envio.strftime('%d/%m/%Y %H:%M'),
            data_resgate=data_resgate.strftime('%d/%m/%Y')
        ))

    return render_template('investejovem.html')

# Página de simulação
@app.route('/simulacao')
def simulacao():
    try:
        # Recebe os dados da URL
        objetivo = request.args.get('objetivo')
        valor_inicial = float(request.args.get('valor_inicial'))
        valor_mensal = float(request.args.get('valor_mensal'))
        tempo = int(request.args.get('tempo'))
        resultado = float(request.args.get('resultado'))
        tipo_investimento = request.args.get('tipo_investimento')
        data_envio = request.args.get('data_envio')
        data_resgate = request.args.get('data_resgate')
    except (ValueError, TypeError):
        return "Dados inválidos fornecidos para a simulação.", 400

    # Cria o gráfico
    grafico = criar_grafico(valor_inicial, valor_mensal, tempo, resultado)

    return render_template(
        'simulacao.html',
        grafico_html=grafico.to_html(full_html=False),
        resultado=resultado,
        tipo_investimento=tipo_investimento,
        objetivo=objetivo,
        valor_inicial=valor_inicial,
        valor_mensal=valor_mensal,
        tempo=tempo,
        data_envio=data_envio,
        data_resgate=data_resgate
    )

# Função para criar o gráfico
def criar_grafico(valor_inicial, valor_mensal, tempo, resultado):
    grafico = go.Figure()

    # Adiciona as barras e linha
    grafico.add_trace(go.Bar(
        x=[f'Mês {i+1}' for i in range(tempo)],
        y=[valor_inicial + i * valor_mensal for i in range(tempo)],
        name='Investimento Acumulado',
        marker_color='purple'
    ))

# Estiliza o gráfico
    grafico.update_traces(
    marker=dict(
        line=dict(width=1, color='white'),
        opacity=0.8
    ),
    width=0.5  # Ajusta a largura para deixar as colunas mais separadas
)
    grafico.update_layout(
    title=dict(
        text='',
        font=dict(color='white'),
        x=0.5
    ),
    xaxis=dict(
        title='Meses',
        titlefont=dict(color='white'),
        tickfont=dict(color='white')
    ),
    yaxis=dict(
        title='Valor (R$)',
        titlefont=dict(color='white'),
        tickfont=dict(color='white')
    ),
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    margin=dict(l=20, r=20, t=40, b=20),
    barmode='group'
)

    return grafico

# Função para calcular rendimento
def calcular_rendimento_personalizado(objetivo, valor_inicial, valor_mensal, tempo):
    taxas = {
        'Estudos': (0.10, 'Renda Fixa (Tesouro Direto, CDB)'),
        'Carros': (0.08, 'Renda Fixa (Tesouro Direto, CDB)'),
        'Casa Propria': (0.09, 'Renda Fixa (Tesouro Direto IPCA+, LCI)'),
        'Entreterimento': (0.07, 'Fundos de Investimento, Poupança'),
        'Viagens': (0.08, 'Fundos de Investimento, Poupança'),
        'Fundo de Emergencia': (0.05, 'Poupança, Tesouro Selic'),
        'Saude': (0.06, 'Poupança, Tesouro IPCA'),
    }
    taxa_anual, tipo_investimento = taxas.get(objetivo, (0.05, 'Investimento não especificado'))
    taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1
    montante = valor_inicial

    for _ in range(tempo):
        montante += valor_mensal
        montante *= (1 + taxa_mensal)

    return round(montante, 2), tipo_investimento

# Página de consulta
@app.route("/consultar")
def consulta():
    return render_template("consultar.html")

@app.route("/plataformas")
def plataformas():
    return render_template("plataformas.html")

