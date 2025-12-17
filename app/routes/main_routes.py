"""메인 페이지 라우트"""

from flask import Blueprint, render_template, request
from flask import current_app

from app.services.pr_service import PRService
from app.utils.validators import validate_pr_state, validate_pr_type
from app.exceptions import ValidationError

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """메인 페이지 - PR 목록"""
    try:
        # 입력 검증
        state = validate_pr_state(
            request.args.get("state", current_app.config.get("DEFAULT_PR_STATE", "open"))
        )
        pr_type = validate_pr_type(request.args.get("type", "authored"))
        
        # 서비스 레이어를 통한 비즈니스 로직 처리
        pr_service = PRService()
        repo = pr_service.get_repo_info()
        owner = repo["owner"]
        name = repo["name"]
        
        # PR 목록 조회
        prs = pr_service.get_prs_by_type(pr_type=pr_type, state=state)
        
        return render_template(
            "index.html",
            prs=prs,
            owner=owner,
            name=name,
            state=state,
            pr_type=pr_type,
            config=current_app.config,
        )
    
    except ValidationError:
        # 검증 에러는 에러 핸들러가 처리
        raise
    except Exception as e:
        current_app.logger.error(f"메인 페이지 로드 실패: {str(e)}", exc_info=True)
        raise

