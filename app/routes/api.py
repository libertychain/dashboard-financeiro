from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.services.financial_service import FinancialService

api = Blueprint('api', __name__)

@api.route('/api/user/theme', methods=['POST'])
def update_user_theme():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    theme = data.get('theme')
    
    user_model = User()
    success = user_model.update_theme_preference(session['user_id'], theme)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Erro ao atualizar tema'}), 500

@api.route('/api/receita', methods=['POST'])
def add_receita():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    descricao = data.get('descricao')
    valor = data.get('valor')
    data_transacao = data.get('data')
    categoria_id = data.get('categoria_id')
    
    if not all([descricao, valor, data_transacao]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    financial_service = FinancialService()
    try:
        receita_id = financial_service.add_receita(
            session['user_id'], descricao, valor, data_transacao, categoria_id
        )
        return jsonify({'success': True, 'id': receita_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/despesa', methods=['POST'])
def add_despesa():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    descricao = data.get('descricao')
    valor = data.get('valor')
    data_transacao = data.get('data')
    categoria_id = data.get('categoria_id')
    
    if not all([descricao, valor, data_transacao]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    financial_service = FinancialService()
    try:
        despesa_id = financial_service.add_despesa(
            session['user_id'], descricao, valor, data_transacao, categoria_id
        )
        return jsonify({'success': True, 'id': despesa_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
