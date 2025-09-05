from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.database import Database

class User(UserMixin):
    def __init__(self, user_id=None, username=None, email=None, password_hash=None):
        self.db = Database()
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def create_user(self, username, email, password):
        """Cria um novo usuário"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            
            # Criar categorias padrão para o usuário
            categorias_receita = [
                ('Salário', '#28a745'),
                ('Freelancer', '#20c997'),
                ('Investimentos', '#17a2b8'),
                ('Outros', '#6c757d')
            ]
            
            categorias_despesa = [
                ('Alimentação', '#dc3545'),
                ('Transporte', '#fd7e14'),
                ('Moradia', '#ffc107'),
                ('Saúde', '#e83e8c'),
                ('Educação', '#6610f2'),
                ('Lazer', '#20c997'),
                ('Outros', '#6c757d')
            ]
            
            for cat_nome, cat_cor in categorias_receita:
                cursor.execute('''
                    INSERT INTO categorias_receita (nome, cor, user_id)
                    VALUES (?, ?, ?)
                ''', (cat_nome, cat_cor, user_id))
            
            for cat_nome, cat_cor in categorias_despesa:
                cursor.execute('''
                    INSERT INTO categorias_despesa (nome, cor, user_id)
                    VALUES (?, ?, ?)
                ''', (cat_nome, cat_cor, user_id))
            
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Autentica um usuário"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            return {'id': user[0], 'username': user[1]}
        return None
    
    def get_user_by_id(self, user_id):
        """Retorna usuário pelo ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, theme_preference FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'theme_preference': user[3]
            }
        return None
    
    def update_theme_preference(self, user_id, theme):
        """Atualiza a preferência de tema do usuário"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET theme_preference = ? WHERE id = ?
            ''', (theme, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
