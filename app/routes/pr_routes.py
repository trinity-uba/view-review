"""PR 관련 라우트"""

from flask import Blueprint, render_template, request
from flask import current_app

from app.services.pr_service import PRService
from app.utils.validators import validate_pr_number
from app.exceptions import NotFoundError

pr_bp = Blueprint('pr', __name__, url_prefix='/pr')


@pr_bp.route("/<int:pr_number>")
def pr_detail(pr_number):
    """PR 상세 페이지 - 리뷰 코멘트 표시"""
    try:
        # 입력 검증
        pr_number = validate_pr_number(pr_number)
        include_resolved = request.args.get("include_resolved", "false").lower() == "true"
        compact_mode = request.args.get("compact_mode", "false").lower() == "true"
        
        # 서비스 레이어를 통한 비즈니스 로직 처리
        pr_service = PRService()
        repo = pr_service.get_repo_info()
        owner = repo["owner"]
        name = repo["name"]
        
        # PR 상세 정보 조회
        pr_data = pr_service.get_pr_with_comments(
            pr_number=pr_number,
            include_resolved=include_resolved
        )
        
        return render_template(
            "pr_detail.html",
            pr=pr_data,
            owner=owner,
            name=name,
            include_resolved=include_resolved,
            compact_mode=compact_mode,
            config=current_app.config,
        )
    
    except NotFoundError:
        # NotFoundError는 에러 핸들러가 처리
        raise
    except Exception as e:
        current_app.logger.error(
            f"PR 상세 페이지 로드 실패: PR #{pr_number}, {str(e)}",
            exc_info=True
        )
        raise

