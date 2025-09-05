class BancoIntegration {
    constructor() {
        this.contas = [];
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.carregarContas();
    }
    
    setupEventListeners() {
        const adicionarContaBtn = document.getElementById('adicionar-conta-button');
        if (adicionarContaBtn) {
            adicionarContaBtn.addEventListener('click', () => {
                this.adicionarConta();
            });
        }
        
        const sincronizarBtn = document.getElementById('sincronizar-contas-button');
        if (sincronizarBtn) {
            sincronizarBtn.addEventListener('click', () => {
                this.sincronizarTodasContas();
            });
        }
    }
    
    async adicionarConta() {
        const nome = document.getElementById('conta-nome').value;
        const banco = document.getElementById('conta-banco').value;
        const agencia = document.getElementById('conta-agencia').value;
        const conta = document.getElementById('conta-numero').value;
        const tipo = document.getElementById('conta-tipo').value;
        const token = document.getElementById('conta-token').value;
        
        if (!nome || !banco || !agencia || !conta) {
            this.showAlert('Preencha todos os campos obrigatórios', 'danger');
            return;
        }
        
        try {
            const response = await fetch('/api/contas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nome,
                    banco,
                    agencia,
                    conta,
                    tipo,
                    token
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Conta adicionada com sucesso!', 'success');
                this.limparFormulario();
                this.carregarContas();
            } else {
                this.showAlert(data.error || 'Erro ao adicionar conta', 'danger');
            }
        } catch (error) {
            this.showAlert('Erro ao adicionar conta: ' + error.message, 'danger');
        }
    }
    
    async sincronizarTodasContas() {
        try {
            const response = await fetch('/api/contas/sincronizar', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Contas sincronizadas com sucesso!', 'success');
                this.carregarContas();
            } else {
                this.showAlert(data.error || 'Erro ao sincronizar contas', 'danger');
            }
        } catch (error) {
            this.showAlert('Erro ao sincronizar contas: ' + error.message, 'danger');
        }
    }
    
    async carregarContas() {
        try {
            const response = await fetch('/api/contas');
            const data = await response.json();
            
            if (data.success) {
                this.contas = data.contas;
                this.renderizarContas();
            }
        } catch (error) {
            console.error('Erro ao carregar contas:', error);
        }
    }
    
    renderizarContas() {
        const container = document.getElementById('lista-contas');
        if (!container) return;
        
        if (this.contas.length === 0) {
            container.innerHTML = '<p>Nenhuma conta cadastrada.</p>';
            return;
        }
        
        const html = this.contas.map(conta => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">${conta.nome}</h5>
                            <p class="card-text">
                                ${conta.banco} - Agência: ${conta.agencia} - Conta: ${conta.conta}
                            </p>
                        </div>
                        <div>
                            <span class="badge bg-primary">${conta.tipo}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    limparFormulario() {
        document.getElementById('conta-nome').value = '';
        document.getElementById('conta-banco').value = '';
        document.getElementById('conta-agencia').value = '';
        document.getElementById('conta-numero').value = '';
        document.getElementById('conta-tipo').value = 'corrente';
        document.getElementById('conta-token').value = '';
    }
    
    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new BancoIntegration();
});
