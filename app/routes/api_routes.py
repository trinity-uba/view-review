"""API 엔드포인트 라우트"""

from flask import Blueprint, request, jsonify
from flask import current_app

from app.services.comment_service import CommentService
from app.services.pr_service import PRService
from app.utils.validators import validate_pr_number, validate_comment_body
from app.exceptions import ValidationError, NotFoundError
from app.database import db, CommentCheck

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route("/health")
def health():
    """헬스체크 엔드포인트"""
    return jsonify({
        "status": "ok",
        "service": "code-review-checker"
    })


@api_bp.route("/pr/<int:pr_number>/reply", methods=["POST"])
def add_reply(pr_number):
    """리뷰 코멘트에 답글 추가 (API)"""
    try:
        # 입력 검증
        pr_number = validate_pr_number(pr_number)
        comment_id = request.form.get("comment_id")
        body = request.form.get("body", "").strip()
        
        # 코멘트 본문 검증
        body = validate_comment_body(body)
        
        if not comment_id:
            raise ValidationError("comment_id가 필요합니다.", field="comment_id")
        
        # 서비스 레이어를 통한 비즈니스 로직 처리
        comment_service = CommentService()
        result = comment_service.add_reply_to_comment(
            pr_number=pr_number,
            comment_id=comment_id,
            body=body
        )
        
        return jsonify({"success": True, "data": result})
    
    except ValidationError as e:
        # 검증 에러는 JSON으로 응답
        return jsonify({"success": False, "error": e.message}), 400
    except Exception as e:
        current_app.logger.error(
            f"답글 작성 실패: PR #{pr_number}, {str(e)}",
            exc_info=True
        )
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/pr/<int:pr_number>/comments/<comment_id>/check", methods=["POST", "GET", "DELETE"])
def toggle_comment_check(pr_number, comment_id):
    """코멘트 체크 상태 저장/조회/삭제 (API)
    
    POST: 체크 상태 저장 또는 업데이트
    GET: 체크 상태 조회
    DELETE: 체크 상태 삭제 (체크 해제)
    """
    try:
        # 입력 검증
        pr_number = validate_pr_number(pr_number)
        
        if not comment_id:
            raise ValidationError("comment_id가 필요합니다.", field="comment_id")
        
        # 저장소 정보 가져오기
        pr_service = PRService()
        repo = pr_service.get_repo_info()
        repo_owner = repo["owner"]
        repo_name = repo["name"]
        
        if request.method == "GET":
            # 체크 상태 조회
            comment_check = CommentCheck.query.filter_by(
                pr_number=pr_number,
                comment_id=str(comment_id)
            ).first()
            
            if comment_check:
                return jsonify({
                    "success": True,
                    "data": {
                        "is_checked": comment_check.is_checked,
                        "checked_at": comment_check.updated_at.isoformat() if comment_check.updated_at else None
                    }
                })
            else:
                return jsonify({
                    "success": True,
                    "data": {
                        "is_checked": False,
                        "checked_at": None
                    }
                })
        
        elif request.method == "POST":
            # 체크 상태 저장 또는 업데이트
            is_checked = request.json.get("is_checked", True) if request.is_json else True
            
            # 기존 레코드 조회
            comment_check = CommentCheck.query.filter_by(
                pr_number=pr_number,
                comment_id=str(comment_id)
            ).first()
            
            if comment_check:
                # 기존 레코드 업데이트
                comment_check.is_checked = is_checked
                db.session.commit()
                current_app.logger.info(
                    f"코멘트 체크 상태 업데이트: PR #{pr_number}, comment_id={comment_id}, checked={is_checked}"
                )
            else:
                # 새 레코드 생성
                comment_check = CommentCheck(
                    pr_number=pr_number,
                    comment_id=str(comment_id),
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    is_checked=is_checked
                )
                db.session.add(comment_check)
                db.session.commit()
                current_app.logger.info(
                    f"코멘트 체크 상태 저장: PR #{pr_number}, comment_id={comment_id}, checked={is_checked}"
                )
            
            return jsonify({
                "success": True,
                "data": comment_check.to_dict()
            })
        
        elif request.method == "DELETE":
            # 체크 상태 삭제 (체크 해제)
            comment_check = CommentCheck.query.filter_by(
                pr_number=pr_number,
                comment_id=str(comment_id)
            ).first()
            
            if comment_check:
                db.session.delete(comment_check)
                db.session.commit()
                current_app.logger.info(
                    f"코멘트 체크 상태 삭제: PR #{pr_number}, comment_id={comment_id}"
                )
            
            return jsonify({
                "success": True,
                "message": "체크 상태가 삭제되었습니다."
            })
    
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"코멘트 체크 상태 처리 실패: PR #{pr_number}, comment_id={comment_id}, {str(e)}",
            exc_info=True
        )
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/pr/<int:pr_number>/comments/checks", methods=["GET"])
def get_all_comment_checks(pr_number):
    """PR의 모든 코멘트 체크 상태 조회 (API)
    
    한 번에 모든 코멘트의 체크 상태를 조회하여 프론트엔드에서 효율적으로 사용할 수 있도록 합니다.
    """
    try:
        # 입력 검증
        pr_number = validate_pr_number(pr_number)
        
        # 해당 PR의 모든 체크 상태 조회
        comment_checks = CommentCheck.query.filter_by(
            pr_number=pr_number,
            is_checked=True
        ).all()
        
        # 코멘트 ID를 키로 하는 딕셔너리로 변환
        checks_dict = {
            check.comment_id: {
                "is_checked": check.is_checked,
                "checked_at": check.updated_at.isoformat() if check.updated_at else None
            }
            for check in comment_checks
        }
        
        return jsonify({
            "success": True,
            "data": checks_dict
        })
    
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), 400
    except Exception as e:
        current_app.logger.error(
            f"코멘트 체크 상태 조회 실패: PR #{pr_number}, {str(e)}",
            exc_info=True
        )
        return jsonify({"success": False, "error": str(e)}), 500

