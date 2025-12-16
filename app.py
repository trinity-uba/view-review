#!/usr/bin/env python3
"""
코드 리뷰 체커 - GitHub PR 리뷰 코멘트 조회 웹 애플리케이션

이 파일은 새로운 모듈화된 구조(app/)를 사용합니다.
기존 코드와의 호환성을 위해 유지되며, 모든 라우트는 app/ 디렉토리의 Blueprint로 관리됩니다.
"""

from app import create_app

# 애플리케이션 팩토리를 사용하여 앱 생성
# 모든 설정, 로깅, 에러 핸들러, 라우트는 app/__init__.py에서 처리됩니다.


if __name__ == "__main__":
    # 애플리케이션 생성 (모든 초기화는 app/__init__.py에서 처리)
    app = create_app()
    
    # 개발 서버 실행
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )
