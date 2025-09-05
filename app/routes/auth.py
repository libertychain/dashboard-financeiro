from flask import Blueprint, request, jsonify, redirect, url_for, session
from app.models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
    
    user_model = User()
    user = user_model.authenticate_user(username, password)
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'error': 'Usuário ou senha inválidos'}), 401

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    
    user_model = User()
    user_id = user_model.create_user(username, email, password)
    
    if user_id:
        return jsonify({'success': True, 'user_id': user_id})
    else:
        return jsonify({'error': 'Erro ao criar usuário'}), 400
