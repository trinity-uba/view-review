"""코멘트 관련 비즈니스 로직 서비스"""

from typing import Dict, Any, Optional
from flask import current_app

from github import GitHubAPI
from app.exceptions import ValidationError


class CommentService:
    """코멘트 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, github_api: Optional[GitHubAPI] = None):
        """
        Args:
            github_api: GitHubAPI 인스턴스 (None이면 새로 생성)
        """
        self.github_api = github_api or GitHubAPI()
    
    def add_reply_to_comment(
        self,
        pr_number: int,
        comment_id: str,
        body: str
    ) -> Dict[str, Any]:
        """
        리뷰 코멘트에 답글 추가
        
        Args:
            pr_number: PR 번호
            comment_id: 원본 코멘트 ID
            body: 답글 내용
        
        Returns:
            생성된 답글 정보
        
        Raises:
            ValidationError: 입력 검증 실패 시
        """
        current_app.logger.info(
            f"답글 작성 요청: PR #{pr_number}, comment_id={comment_id}"
        )
        
        # 입력 검증
        if not comment_id:
            raise ValidationError("comment_id가 필요합니다.", field="comment_id")
        
        if not body or not body.strip():
            raise ValidationError("답글 내용이 필요합니다.", field="body")
        
        body = body.strip()
        
        try:
            repo = self.github_api.get_repo_info()
            owner = repo["owner"]
            name = repo["name"]
            
            # 답글 작성
            result = self.github_api.add_reply_to_comment(
                owner=owner,
                name=name,
                pr_number=pr_number,
                comment_id=comment_id,
                body=body
            )
            
            current_app.logger.info(
                f"답글 작성 완료: PR #{pr_number}, comment_id={comment_id}"
            )
            
            return result
            
        except Exception as e:
            current_app.logger.error(
                f"답글 작성 실패: PR #{pr_number}, {str(e)}",
                exc_info=True
            )
            raise

