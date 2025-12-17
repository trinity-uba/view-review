"""로깅 유틸리티"""

import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask


def setup_logging(app: Flask) -> None:
    """
    애플리케이션 로깅 설정
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    # 기본 로깅 레벨 설정
    if app.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    app.logger.setLevel(log_level)
    
    # 기존 핸들러 제거 (중복 방지)
    app.logger.handlers.clear()
    
    # 콘솔 핸들러 (항상 추가)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # 파일 핸들러 (프로덕션 환경)
    if not app.debug:
        # 프로젝트 루트 디렉토리에 logs 폴더 생성
        # app.root_path는 Flask 앱의 루트 경로 (app/ 디렉토리)
        # 프로젝트 루트는 그 상위 디렉토리
        project_root = os.path.dirname(app.root_path)
        logs_dir = os.path.join(project_root, 'logs')
        
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
        
        log_file_path = os.path.join(logs_dir, 'viewreview.log')
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10240000,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)
        
        app.logger.info('ViewReview 애플리케이션 시작')
    else:
        app.logger.debug('ViewReview 개발 모드로 시작')

