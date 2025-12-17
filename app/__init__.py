"""애플리케이션 팩토리 모듈"""

import os
from flask import Flask
from config import get_config
from app.utils.logger import setup_logging
from app.utils.error_handlers import register_error_handlers
from app.utils.cache import init_cache
from app.database import db


def create_app(config_name: str = None) -> Flask:
    """
    Flask 애플리케이션 팩토리
    
    Args:
        config_name: 설정 환경 이름 (development, production, testing 등)
    
    Returns:
        설정된 Flask 애플리케이션 인스턴스
    """
    # 프로젝트 루트 디렉토리 경로 (app.py가 있는 위치)
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    
    # 설정 로드
    config = get_config(config_name)
    app.config.from_object(config)
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # 데이터베이스 테이블 생성 (개발 환경에서만 자동 생성)
    with app.app_context():
        db.create_all()
    
    # 로깅 설정
    setup_logging(app)
    
    # 캐시 초기화
    init_cache(app)
    
    # 에러 핸들러 등록
    register_error_handlers(app)
    
    # Jinja2 필터 등록
    from app.utils.formatters import format_time
    app.jinja_env.filters['format_time'] = format_time
    
    # Blueprint 라우트 등록
    from app.routes import main_bp, pr_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(pr_bp)
    app.register_blueprint(api_bp)
    
    # 레거시 엔드포인트 (기존 엔드포인트와의 호환성)
    @app.route("/pr/<int:pr_number>/reply", methods=["POST"])
    def legacy_add_reply(pr_number):
        """레거시 답글 엔드포인트 (하위 호환성)"""
        from app.routes.api_routes import add_reply
        return add_reply(pr_number)
    
    @app.route("/health")
    def legacy_health():
        """레거시 헬스체크 엔드포인트 (하위 호환성)"""
        from app.routes.api_routes import health
        return health()
    
    app.logger.info('ViewReview 애플리케이션 초기화 완료')
    
    return app

