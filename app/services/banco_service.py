from app.models.banco import BancoAPI
from app.services.financial_service import FinancialService

class BancoService:
    def __init__(self):
        self.banco_api = BancoAPI()
        self.financial_service = FinancialService()
    
    def sincronizar_todas_contas(self, user_id):
        """Sincroniza todas as contas bancárias do usuário"""
        conn = self.banco_api.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM contas_bancarias WHERE user_id = ?', (user_id,))
        contas = cursor.fetchall()
        conn.close()
        
        resultados = []
        for conta in contas:
            conta_id = conta[0]
            try:
                transacoes = self.banco_api.sincronizar_transacoes(conta_id)
                resultados.append({
                    'conta_id': conta_id,
                    'status': 'sucesso',
                    'transacoes': len(transacoes)
                })
            except Exception as e:
                resultados.append({
                    'conta_id': conta_id,
                    'status': 'erro',
                    'mensagem': str(e)
                })
        
        return resultados
    
    def get_saldo_consolidado(self, user_id):
        """Retorna saldo consolidado de todas as contas"""
        contas = self.banco_api.get_saldo_contas(user_id)
        
        # Adicionar saldo atual baseado nas transações
        for _, conta in contas.iterrows():
            # Calcular saldo atual baseado nas transações
            # (Esta é uma simplificação, na prática seria mais complexo)
            pass
        
        return contas
