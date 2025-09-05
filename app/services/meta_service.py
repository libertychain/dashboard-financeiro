from app.models.meta import Meta
from app.services.financial_service import FinancialService

class MetaService:
    def __init__(self):
        self.meta_model = Meta()
        self.financial_service = FinancialService()
    
    def calcular_progresso_metas(self, user_id):
        """Calcula o progresso de todas as metas do usuário"""
        metas = self.meta_model.listar_metas(user_id)
        
        # Para cada meta, calcular o progresso baseado nas transações
        for _, meta in metas.iterrows():
            if meta['tipo'] == 'economia':
                # Calcular economia total (receitas - despesas)
                resumo = self.financial_service.get_financial_summary(user_id)
                economia = resumo['saldo']
                self.meta_model.atualizar_progresso(meta['id'], economia)
            
            elif meta['tipo'] == 'receita':
                # Calcular total de receitas
                receitas = self.financial_service.get_receitas(user_id)
                total_receitas = receitas['valor'].sum()
                self.meta_model.atualizar_progresso(meta['id'], total_receitas)
            
            elif meta['tipo'] == 'despesa':
                # Calcular total de despesas
                despesas = self.financial_service.get_despesas(user_id)
                total_despesas = despesas['valor'].sum()
                self.meta_model.atualizar_progresso(meta['id'], total_despesas)
        
        return self.meta_model.listar_metas(user_id)
