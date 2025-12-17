"""에러 핸들러 유틸리티"""

from flask import render_template, request
from app.exceptions import ViewReviewError, GitHubAPIError, ValidationError, NotFoundError


def register_error_handlers(app):
    """
    Flask 애플리케이션에 에러 핸들러 등록
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    
    @app.errorhandler(GitHubAPIError)
    def handle_github_error(e):
        """GitHub API 에러 처리"""
        app.logger.error(
            f"GitHub API 에러 발생: {e.message} (상태 코드: {e.status_code})",
            exc_info=True,
            extra={
                'url': request.url,
                'method': request.method,
                'status_code': e.status_code
            }
        )
        return render_template(
            'error.html',
            error_title="GitHub 연결 오류",
            error_message=e.message,
            config=app.config
        ), e.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """입력 검증 에러 처리"""
        app.logger.warning(
            f"입력 검증 실패: {e.message} (필드: {e.field})",
            extra={
                'url': request.url,
                'method': request.method,
                'field': e.field
            }
        )
        return render_template(
            'error.html',
            error_title="입력 오류",
            error_message=e.message,
            config=app.config
        ), 400
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        """리소스 없음 에러 처리"""
        app.logger.info(
            f"리소스를 찾을 수 없음: {e.resource_type} #{e.resource_id}",
            extra={
                'url': request.url,
                'method': request.method,
                'resource_type': e.resource_type,
                'resource_id': e.resource_id
            }
        )
        return render_template(
            'error.html',
            error_title=f"{e.resource_type}을(를) 찾을 수 없습니다",
            error_message=e.message,
            config=app.config
        ), 404
    
    @app.errorhandler(404)
    def handle_404(e):
        """404 에러 처리"""
        app.logger.info(
            f"페이지를 찾을 수 없음: {request.url}",
            extra={'url': request.url, 'method': request.method}
        )
        return render_template(
            'error.html',
            error_title="페이지를 찾을 수 없습니다",
            error_message="요청하신 페이지가 존재하지 않습니다.",
            config=app.config
        ), 404
    
    @app.errorhandler(500)
    def handle_500(e):
        """500 에러 처리"""
        app.logger.error(
            f"서버 내부 오류 발생: {str(e)}",
            exc_info=True,
            extra={
                'url': request.url,
                'method': request.method
            }
        )
        return render_template(
            'error.html',
            error_title="서버 오류",
            error_message="예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            config=app.config
        ), 500
    
    @app.errorhandler(Exception)
    def handle_generic_error(e):
        """기타 예외 처리"""
        app.logger.error(
            f"예상치 못한 오류 발생: {type(e).__name__}: {str(e)}",
            exc_info=True,
            extra={
                'url': request.url,
                'method': request.method,
                'exception_type': type(e).__name__
            }
        )
        return render_template(
            'error.html',
            error_title="오류 발생",
            error_message=f"예상치 못한 오류가 발생했습니다: {str(e)}",
            config=app.config
        ), 500

