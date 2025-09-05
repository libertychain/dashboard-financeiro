from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.services.financial_service import FinancialService
from app.services.chart_service import ChartService

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/api/dashboard/summary')
def get_dashboard_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    financial_service = FinancialService()
    summary = financial_service.get_financial_summary(user_id)
    
    return jsonify(summary)

@dashboard.route('/api/dashboard/charts/evolucao')
def get_evolucao_chart():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    chart_service = ChartService()
    fig = chart_service.create_evolucao_chart(user_id)
    
    return jsonify(fig.to_dict())

@dashboard.route('/api/dashboard/charts/categorias')
def get_categorias_chart():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    chart_service = ChartService()
    fig = chart_service.create_categorias_chart(user_id)
    
    return jsonify(fig.to_dict())

@dashboard.route('/api/dashboard/transacoes/recentes')
def get_recent_transactions():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    financial_service = FinancialService()
    
    # Obter últimas 10 transações (receitas e despesas)
    receitas = financial_service.get_receitas(user_id)
    despesas = financial_service.get_despesas(user_id)
    
    # Combinar e ordenar
    receitas['tipo'] = 'receita'
    despesas['tipo'] = 'despesa'
    
    transacoes = pd.concat([receitas, despesas])
    transacoes = transacoes.sort_values('data', ascending=False).head(10)
    
    return jsonify(transacoes.to_dict('records'))
