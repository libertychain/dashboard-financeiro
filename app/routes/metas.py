from flask import Blueprint, request, jsonify, session
from app.models.meta import Meta

metas = Blueprint('metas', __name__)

@metas.route('/api/metas', methods=['GET'])
def get_metas():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    meta_model = Meta()
    metas = meta_model.listar_metas(user_id)
    
    return jsonify(metas.to_dict('records'))

@metas.route('/api/metas', methods=['POST'])
def create_meta():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    nome = data.get('nome')
    valor_meta = data.get('valor_meta')
    data_limite = data.get('data_limite')
    tipo = data.get('tipo', 'economia')
    
    if not all([nome, valor_meta]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    meta_model = Meta()
    try:
        meta_id = meta_model.criar_meta(
            session['user_id'], nome, valor_meta, data_limite, tipo
        )
        return jsonify({'success': True, 'id': meta_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metas.route('/api/metas/<int:meta_id>/progresso', methods=['POST'])
def atualizar_progresso(meta_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    valor_adicional = data.get('valor_adicional')
    
    if not valor_adicional:
        return jsonify({'error': 'Valor adicional é obrigatório'}), 400
    
    meta_model = Meta()
    success = meta_model.atualizar_progresso(meta_id, valor_adicional)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Erro ao atualizar progresso'}), 500
