import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime
import os
import io
import csv
import json
from fpdf import FPDF
from flask import send_file
import tempfile

print("Iniciando Dashboard Financeiro...")

# Configuração da aplicação
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions'] = True
server = app.server

# Inicializar banco de dados
def init_database():
    """Inicializa o banco de dados e cria as tabelas se não existirem"""
    conn = sqlite3.connect('financeiro.db')
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabela de metas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    
    # Tabela de contas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            saldo REAL NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    
    # Verificar se já existe usuário admin
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        # Inserir usuário admin
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))
        print("Usuário admin criado!")
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

init_database()

# Rota para download do PDF
@server.route('/download-pdf')
def download_pdf():
    try:
        # Criar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatório Financeiro", ln=1, align="C")
        pdf.cell(200, 10, txt="Data: " + datetime.now().strftime("%d/%m/%Y"), ln=1, align="C")
        pdf.ln(10)
        
        # Adicionar dados de metas
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Metas Financeiras:", ln=1, align="L")
        pdf.set_font("Arial", size=9)
        
        # Buscar metas no banco
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        # Garantir que a tabela metas existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                valor REAL NOT NULL,
                data_criacao TEXT NOT NULL
            )
        ''')
        
        cursor.execute("SELECT nome, valor, data_criacao FROM metas")
        metas = cursor.fetchall()
        conn.close()
        
        for meta in metas:
            pdf.cell(200, 8, txt=f"- {meta[0]}: R$ {meta[1]:.2f} (Criada em: {meta[2]})", ln=1, align="L")
        
        pdf.ln(10)
        
        # Adicionar dados de contas
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Contas Bancárias:", ln=1, align="L")
        pdf.set_font("Arial", size=9)
        
        # Buscar contas no banco
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        # Garantir que a tabela contas existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                saldo REAL NOT NULL,
                data_criacao TEXT NOT NULL
            )
        ''')
        
        cursor.execute("SELECT nome, saldo, data_criacao FROM contas")
        contas = cursor.fetchall()
        conn.close()
        
        for conta in contas:
            pdf.cell(200, 8, txt=f"- {conta[0]}: R$ {conta[1]:.2f} (Criada em: {conta[2]})", ln=1, align="L")
        
        # Salvar em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name, 'F')
        temp_file.close()
        
        # Enviar o arquivo
        return send_file(temp_file.name, as_attachment=True, download_name="relatorio_financeiro.pdf")
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return str(e), 500

# Layout de login
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Dashboard Financeiro", className="text-center mb-4", style={'color': '#2c3e50'}),
                html.P("Gerencie suas finanças pessoais com inteligência", 
                       className="text-center text-muted mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Login", className="card-title text-center mb-4"),
                        
                        html.Div([
                            dbc.Label("Usuário", className="form-label"),
                            dbc.Input(
                                id="username-input",
                                type="text",
                                placeholder="Digite seu usuário",
                                className="mb-3"
                            ),
                            
                            dbc.Label("Senha", className="form-label"),
                            dbc.Input(
                                id="password-input",
                                type="password",
                                placeholder="Digite sua senha",
                                className="mb-3"
                            ),
                            
                            dbc.Button(
                                "Entrar",
                                id="login-button",
                                color="primary",
                                className="w-100"
                            ),
                        ]),
                        
                        html.Div(id="login-error", className="text-danger text-center mt-2"),
                        
                        html.Hr(),
                        
                        html.P("Use admin/admin para entrar", className="text-center text-info")
                    ])
                ], style={'borderRadius': '15px'})
            ], style={
                'maxWidth': '400px',
                'margin': '100px auto',
                'padding': '20px'
            })
        ], width=12)
    ])
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# Layout principal após login
def create_main_layout(theme='light'):
    # Definir cores com base no tema
    bg_color = '#343a40' if theme == 'dark' else '#f8f9fa'
    text_color = '#ffffff' if theme == 'dark' else '#2c3e50'
    card_color = '#4e5d6c' if theme == 'dark' else 'light'
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard Financeiro", className="mb-4", style={'color': text_color}),
            ], width=12)
        ]),
        
        # Cards principais
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Saldo Atual", className="card-title", style={'color': text_color}),
                        html.H2("R$ 5.000,00", className="text-primary")
                    ])
                ], color=card_color)
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Receitas", className="card-title", style={'color': text_color}),
                        html.H2("R$ 8.000,00", className="text-success")
                    ])
                ], color=card_color)
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Despesas", className="card-title", style={'color': text_color}),
                        html.H2("R$ 3.000,00", className="text-danger")
                    ])
                ], color=card_color)
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Metas", className="card-title", style={'color': text_color}),
                        html.H2("2", className="text-info")
                    ])
                ], color=card_color)
            ], width=3),
        ], className="mb-4"),
        
        # Menu de funcionalidades
        dbc.Row([
            dbc.Col([
                html.H3("Funcionalidades", className="mb-3", style={'color': text_color}),
            ], width=12)
        ]),
        
        dbc.Row([
            # Metas Financeiras
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-bullseye me-2"),
                            "Metas Financeiras"
                        ], className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.P("Defina e acompanhe seus objetivos financeiros", style={'color': text_color}),
                        html.Hr(),
                        html.Div([
                            html.Strong("Metas Ativas:", style={'color': text_color}),
                            html.Ul([
                                html.Li("Viagem para Europa - R$ 15.000,00", style={'color': text_color}),
                                html.Li("Fundo de Emergência - R$ 10.000,00", style={'color': text_color})
                            ])
                        ]),
                        dbc.Button("Gerenciar Metas", href="/metas", color="primary", className="mt-3")
                    ])
                ], className="h-100", color=card_color)
            ], width=6),
            
            # Contas Bancárias
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-university me-2"),
                            "Contas Bancárias"
                        ], className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.P("Conecte e gerencie suas contas bancárias", style={'color': text_color}),
                        html.Hr(),
                        html.Div([
                            html.Strong("Contas Cadastradas:", style={'color': text_color}),
                            html.Ul([
                                html.Li("Banco do Brasil - R$ 5.000,00", style={'color': text_color})
                            ])
                        ]),
                        dbc.Button("Gerenciar Contas", href="/contas", color="primary", className="mt-3")
                    ])
                ], className="h-100", color=card_color)
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # Relatórios PDF
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-file-pdf me-2"),
                            "Relatórios PDF"
                        ], className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.P("Exporte análises financeiras em PDF", style={'color': text_color}),
                        html.Hr(),
                        html.P("Gere relatórios mensais, por período ou de metas.", style={'color': text_color}),
                        dbc.Button("Gerar Relatórios", href="/relatorios", color="primary", className="mt-3")
                    ])
                ], className="h-100", color=card_color)
            ], width=4),
            
            # Exportação de Dados
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-download me-2"),
                            "Exportar Dados"
                        ], className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.P("Exporte seus dados em vários formatos", style={'color': text_color}),
                        html.Hr(),
                        html.P("CSV, Excel, JSON - Escolha o formato que preferir.", style={'color': text_color}),
                        dbc.Button("Exportar Dados", href="/exportar", color="primary", className="mt-3")
                    ])
                ], className="h-100", color=card_color)
            ], width=4),
            
            # Modo Escuro/Claro
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-palette me-2"),
                            "Personalização"
                        ], className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.P("Alterne entre modo claro e escuro", style={'color': text_color}),
                        html.Hr(),
                        html.P("Escolha o tema que mais te agrada.", style={'color': text_color}),
                        dbc.Button("Alternar Tema", id="theme-toggle-btn", color="primary", className="mt-3")
                    ])
                ], className="h-100", color=card_color)
            ], width=4),
        ], className="mb-4"),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Evolução Financeira", className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='evolucao-grafico')
                    ])
                ], color=card_color)
            ], width=12),
        ], className="mb-4"),
        
        # Últimas transações
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Últimas Transações", className="mb-0", style={'color': text_color})
                    ]),
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Span("Salário", className="fw-bold"),
                                html.Span(" - R$ 5.000,00", className="text-success ms-2"),
                                html.Span(" (01/01/2024)", className="text-muted ms-2")
                            ], className="mb-2"),
                            html.Div([
                                html.Span("Aluguel", className="fw-bold"),
                                html.Span(" - R$ 1.500,00", className="text-danger ms-2"),
                                html.Span(" (02/01/2024)", className="text-muted ms-2")
                            ], className="mb-2")
                        ])
                    ])
                ], color=card_color)
            ], width=12),
        ]),
        
        # Rodapé
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P("Dashboard Financeiro v1.0 - Todos os direitos reservados", 
                       className="text-center text-muted")
            ], width=12)
        ])
    ], fluid=True, style={'backgroundColor': bg_color, 'minHeight': '100vh'})

# Layout inicial - apenas um dcc.Location no layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='login-store', data=False),
    dcc.Store(id='theme-store', data='light'),
    html.Div(id='page-content', children=login_layout)
])

# Callback de login - único callback para login
@callback(
    Output('login-store', 'data'),
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')]
)
def login_user(n_clicks, username, password):
    if n_clicks and username and password:
        if username == "admin" and password == "admin":
            return True  # Login bem sucedido
    return False  # Login falhou ou não tentou

# Callback para redirecionar após login
@callback(
    Output('url', 'pathname'),
    [Input('login-store', 'data')]
)
def redirect_on_login(login_status):
    if login_status:
        return '/dashboard'
    return '/login'

# Callback principal de controle de página
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('login-store', 'data')],
    [State('theme-store', 'data')]
)
def display_page(pathname, login_status, theme):
    # Se não estiver logado, sempre mostra tela de login
    if not login_status:
        return login_layout
    
    # Se estiver logado, mostra a página correspondente
    if pathname == '/dashboard' or pathname == '/':
        return create_main_layout(theme)
    elif pathname == '/metas':
        return create_metas_layout(theme)
    elif pathname == '/contas':
        return create_contas_layout(theme)
    elif pathname == '/relatorios':
        return create_relatorios_layout(theme)
    elif pathname == '/exportar':
        return create_exportar_layout(theme)
    else:
        return create_main_layout(theme)

# Layouts das funcionalidades
def create_metas_layout(theme='light'):
    # Definir cores com base no tema
    bg_color = '#343a40' if theme == 'dark' else '#f8f9fa'
    text_color = '#ffffff' if theme == 'dark' else '#2c3e50'
    card_color = '#4e5d6c' if theme == 'dark' else 'light'
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Metas Financeiras", className="mb-4", style={'color': text_color}),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Minhas Metas", style={'color': text_color}),
                        html.Div(id='lista-metas'),
                        html.Hr(),
                        html.Div([
                            dbc.Label("Nova Meta", className="form-label", style={'color': text_color}),
                            dbc.Input(id='input-nome-meta', placeholder="Nome da meta", className="mb-3"),
                            dbc.Label("Valor da Meta", className="form-label", style={'color': text_color}),
                            dbc.Input(id='input-valor-meta', placeholder="Valor", type="number", className="mb-3"),
                            dbc.Button("Adicionar Meta", id='btn-adicionar-meta', color="primary", className="w-100")
                        ])
                    ])
                ], color=card_color)
            ], width=8)
        ])
    ], fluid=True, style={'backgroundColor': bg_color, 'minHeight': '100vh'})

def create_contas_layout(theme='light'):
    # Definir cores com base no tema
    bg_color = '#343a40' if theme == 'dark' else '#f8f9fa'
    text_color = '#ffffff' if theme == 'dark' else '#2c3e50'
    card_color = '#4e5d6c' if theme == 'dark' else 'light'
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Contas Bancárias", className="mb-4", style={'color': text_color}),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Minhas Contas", style={'color': text_color}),
                        html.Div(id='lista-contas'),
                        html.Hr(),
                        html.Div([
                            dbc.Label("Nome do Banco", className="form-label", style={'color': text_color}),
                            dbc.Input(id='input-nome-banco', placeholder="Nome do banco", className="mb-3"),
                            dbc.Label("Saldo Inicial", className="form-label", style={'color': text_color}),
                            dbc.Input(id='input-saldo-inicial', placeholder="Saldo", type="number", className="mb-3"),
                            dbc.Button("Adicionar Conta", id='btn-adicionar-conta', color="primary", className="w-100")
                        ])
                    ])
                ], color=card_color)
            ], width=8)
        ])
    ], fluid=True, style={'backgroundColor': bg_color, 'minHeight': '100vh'})

def create_relatorios_layout(theme='light'):
    # Definir cores com base no tema
    bg_color = '#343a40' if theme == 'dark' else '#f8f9fa'
    text_color = '#ffffff' if theme == 'dark' else '#2c3e50'
    card_color = '#4e5d6c' if theme == 'dark' else 'light'
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Relatórios PDF", className="mb-4", style={'color': text_color}),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Gerar Relatório", style={'color': text_color}),
                        html.P("Selecione o tipo de relatório que deseja gerar:", style={'color': text_color}),
                        html.Ul([
                            html.Li("Relatório Mensal", style={'color': text_color}),
                            html.Li("Relatório por Período", style={'color': text_color}),
                            html.Li("Relatório de Metas", style={'color': text_color})
                        ]),
                        html.Hr(),
                        html.A("Baixar Relatório PDF", 
                               href="/download-pdf", 
                               className="btn btn-primary", 
                               target="_blank")
                    ])
                ], color=card_color)
            ], width=8)
        ])
    ], fluid=True, style={'backgroundColor': bg_color, 'minHeight': '100vh'})

def create_exportar_layout(theme='light'):
    # Definir cores com base no tema
    bg_color = '#343a40' if theme == 'dark' else '#f8f9fa'
    text_color = '#ffffff' if theme == 'dark' else '#2c3e50'
    card_color = '#4e5d6c' if theme == 'dark' else 'light'
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Exportar Dados", className="mb-4", style={'color': text_color}),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Exportar Transações", style={'color': text_color}),
                        html.P("Selecione o formato de exportação:", style={'color': text_color}),
                        html.Ul([
                            html.Li("CSV - Formato compatível com Excel", style={'color': text_color}),
                            html.Li("Excel - Formato nativo do Excel", style={'color': text_color}),
                            html.Li("JSON - Formato para programadores", style={'color': text_color})
                        ]),
                        html.Hr(),
                        html.Div([
                            dbc.Label("Formato", className="form-label", style={'color': text_color}),
                            dcc.Dropdown(
                                id='dropdown-formato',
                                options=[
                                    {'label': 'CSV', 'value': 'csv'},
                                    {'label': 'Excel', 'value': 'excel'},
                                    {'label': 'JSON', 'value': 'json'}
                                ],
                                value='csv',
                                className="mb-3"
                            ),
                            dbc.Button("Exportar Dados", id='btn-exportar', color="primary", className="w-100")
                        ])
                    ])
                ], color=card_color)
            ], width=8)
        ]),
        dcc.Download(id="download-data")
    ], fluid=True, style={'backgroundColor': bg_color, 'minHeight': '100vh'})

# Callback para o gráfico
@callback(
    Output('evolucao-grafico', 'figure'),
    Input('url', 'pathname')
)
def update_graph(pathname):
    if pathname == '/dashboard':
        # Dados de exemplo
        df = pd.DataFrame({
            'Mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'Receitas': [8000, 8500, 9000, 8200, 8800, 9500],
            'Despesas': [3000, 3200, 3500, 3100, 3300, 3600]
        })
        
        fig = px.line(df, x='Mes', y=['Receitas', 'Despesas'], 
                     title='Evolução Financeira Mensal',
                     color_discrete_map={'Receitas': '#28a745', 'Despesas': '#dc3545'})
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        return fig
    
    return {}

# Callback para tema
@callback(
    Output('theme-store', 'data'),
    [Input('theme-toggle-btn', 'n_clicks')],
    [State('theme-store', 'data')]
)
def toggle_theme(n_clicks, current_theme):
    if n_clicks:
        return 'dark' if current_theme == 'light' else 'light'
    return current_theme

# Callback para atualizar o texto do botão de tema
@callback(
    Output('theme-toggle-btn', 'children'),
    [Input('theme-store', 'data')]
)
def update_theme_button(theme):
    return "Modo Claro" if theme == 'dark' else "Modo Escuro"

# Callback para adicionar meta
@callback(
    Output('lista-metas', 'children'),
    [Input('btn-adicionar-meta', 'n_clicks')],
    [State('input-nome-meta', 'value'),
     State('input-valor-meta', 'value')]
)
def adicionar_meta(n_clicks, nome, valor):
    if n_clicks and nome and valor:
        try:
            # Garantir que a tabela metas existe
            conn = sqlite3.connect('financeiro.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data_criacao TEXT NOT NULL
                )
            ''')
            
            # Inserir nova meta
            data_atual = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO metas (nome, valor, data_criacao) VALUES (?, ?, ?)", 
                          (nome, float(valor), data_atual))
            conn.commit()
            conn.close()
            
            # Retornar mensagem de sucesso
            return dbc.Alert(f"Meta '{nome}' de R$ {valor} adicionada com sucesso!", color="success")
        except Exception as e:
            return dbc.Alert(f"Erro ao adicionar meta: {str(e)}", color="danger")
    
    return ""

# Callback para adicionar conta
@callback(
    Output('lista-contas', 'children'),
    [Input('btn-adicionar-conta', 'n_clicks')],
    [State('input-nome-banco', 'value'),
     State('input-saldo-inicial', 'value')]
)
def adicionar_conta(n_clicks, nome_banco, saldo):
    if n_clicks and nome_banco and saldo:
        try:
            # Garantir que a tabela contas existe
            conn = sqlite3.connect('financeiro.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    saldo REAL NOT NULL,
                    data_criacao TEXT NOT NULL
                )
            ''')
            
            # Inserir nova conta
            data_atual = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO contas (nome, saldo, data_criacao) VALUES (?, ?, ?)", 
                          (nome_banco, float(saldo), data_atual))
            conn.commit()
            conn.close()
            
            # Retornar mensagem de sucesso
            return dbc.Alert(f"Conta '{nome_banco}' com saldo R$ {saldo} adicionada com sucesso!", color="success")
        except Exception as e:
            return dbc.Alert(f"Erro ao adicionar conta: {str(e)}", color="danger")
    
    return ""

# Callback para exportar dados
@callback(
    Output("download-data", "data"),
    [Input('btn-exportar', 'n_clicks')],
    [State('dropdown-formato', 'value')]
)
def exportar_dados(n_clicks, formato):
    if n_clicks:
        try:
            # Dados de exemplo (na prática, buscar do banco)
            dados = [
                {'Data': '01/01/2024', 'Descrição': 'Salário', 'Valor': 5000, 'Tipo': 'Receita'},
                {'Data': '02/01/2024', 'Descrição': 'Aluguel', 'Valor': 1500, 'Tipo': 'Despesa'}
            ]
            
            if formato == 'csv':
                buffer = io.StringIO()
                writer = csv.DictWriter(buffer, fieldnames=dados[0].keys())
                writer.writeheader()
                writer.writerows(dados)
                
                # Obter a string do buffer (sem converter para bytes)
                content = buffer.getvalue()
                
                return dict(content=content, 
                            filename="dados_financeiros.csv", 
                            type="text/csv")
            
            elif formato == 'excel':
                df = pd.DataFrame(dados)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                # Para Excel, mantém como bytes
                content = buffer.getvalue()
                
                return dict(content=content, 
                            filename="dados_financeiros.xlsx", 
                            type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            elif formato == 'json':
                # Converter para string JSON (sem converter para bytes)
                content = json.dumps(dados, ensure_ascii=False)
                
                return dict(content=content, 
                            filename="dados_financeiros.json", 
                            type="application/json")
        except Exception as e:
            print(f"Erro ao exportar dados: {str(e)}")
            return None
    
    return None

print("Dashboard Financeiro pronto!")

if __name__ == '__main__':
    print("Iniciando servidor na porta 8050...")
    app.run(debug=False, host='0.0.0.0', port=8050)
