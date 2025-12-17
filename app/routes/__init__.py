"""라우트 모듈"""

from app.routes.pr_routes import pr_bp
from app.routes.api_routes import api_bp
from app.routes.main_routes import main_bp

__all__ = ['pr_bp', 'api_bp', 'main_bp']

