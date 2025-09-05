from .auth import auth as auth_blueprint
from .dashboard import dashboard as dashboard_blueprint
from .api import api as api_blueprint
from .metas import metas as metas_blueprint
from .relatorios import relatorios as relatorios_blueprint

__all__ = ['auth_blueprint', 'dashboard_blueprint', 'api_blueprint', 'metas_blueprint', 'relatorios_blueprint']
