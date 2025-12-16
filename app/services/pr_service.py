"""PR 관련 비즈니스 로직 서비스"""

from typing import List, Dict, Any, Optional
from markupsafe import Markup
from flask import current_app

from github import GitHubAPI
from app.exceptions import NotFoundError
from app.utils.cache import cached


class PRService:
    """PR 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, github_api: Optional[GitHubAPI] = None):
        """
        Args:
            github_api: GitHubAPI 인스턴스 (None이면 새로 생성)
        """
        self.github_api = github_api or GitHubAPI()
        self._repo_info_cache: Optional[Dict[str, str]] = None
    
    @cached(timeout=3600, key_prefix="repo_info")  # 1시간 캐싱
    def get_repo_info(self) -> Dict[str, str]:
        """
        저장소 정보 조회 (캐싱 적용)
        
        Returns:
            저장소 정보 딕셔너리 (owner, name)
        """
        # 인스턴스 변수 캐시도 유지 (캐시 미스 시 빠른 접근)
        if self._repo_info_cache is None:
            self._repo_info_cache = self.github_api.get_repo_info()
        return self._repo_info_cache
    
    @cached(timeout=300, key_prefix="pr_list")  # 5분 캐싱
    def get_prs_by_type(self, pr_type: str, state: str) -> List[Dict[str, Any]]:
        """
        PR 타입에 따라 목록 조회 (캐싱 적용)
        
        Args:
            pr_type: PR 타입 ("authored" 또는 "reviewed")
            state: PR 상태 ("open", "closed", "merged", "all")
        
        Returns:
            PR 정보 리스트
        """
        current_app.logger.info(f"PR 목록 조회: type={pr_type}, state={state}")
        
        try:
            if pr_type == "reviewed":
                # 내가 리뷰 코멘트를 남긴 PR 목록
                prs = self.github_api.get_prs_with_my_review_comments(state=state)
            else:
                # 내가 작성한 PR 목록 (기본값)
                prs = self.github_api.get_my_pr_list(state=state)
            
            current_app.logger.info(f"PR 목록 조회 완료: {len(prs)}개")
            return prs
            
        except Exception as e:
            current_app.logger.error(f"PR 목록 조회 실패: {str(e)}", exc_info=True)
            raise
    
    @cached(timeout=120, key_prefix="pr_detail")  # 2분 캐싱
    def get_pr_with_comments(
        self,
        pr_number: int,
        include_resolved: bool = False
    ) -> Dict[str, Any]:
        """
        PR 상세 정보와 코멘트 조회 (캐싱 적용)
        
        Args:
            pr_number: PR 번호
            include_resolved: 해결된 코멘트 포함 여부
        
        Returns:
            PR 상세 정보 딕셔너리
        
        Raises:
            NotFoundError: PR을 찾을 수 없는 경우
        """
        current_app.logger.info(
            f"PR 상세 조회: number={pr_number}, include_resolved={include_resolved}"
        )
        
        try:
            repo = self.get_repo_info()
            owner = repo["owner"]
            name = repo["name"]
            
            # PR 코멘트 조회
            pr_data = self.github_api.get_comments_for_pr(
                owner, name, pr_number, include_resolved=include_resolved
            )
            
            if not pr_data:
                raise NotFoundError("PR", str(pr_number))
            
            # 데이터 가공: bodyHTML을 Markup으로 래핑
            pr_data = self._process_pr_data(pr_data)
            
            current_app.logger.info(f"PR 상세 조회 완료: PR #{pr_number}")
            return pr_data
            
        except NotFoundError:
            raise
        except Exception as e:
            current_app.logger.error(
                f"PR 상세 조회 실패: PR #{pr_number}, {str(e)}",
                exc_info=True
            )
            raise
    
    def _process_pr_data(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PR 데이터 가공 (bodyHTML을 Markup으로 변환)
        
        Args:
            pr_data: 원본 PR 데이터
        
        Returns:
            가공된 PR 데이터
        """
        comments = pr_data.get("comments", [])
        if comments:
            for comment in comments:
                body = comment.get("bodyHTML")
                comment["bodyHTML_safe"] = Markup(body) if body else Markup("")
                
                # 댓글도 Markup 처리
                replies = comment.get("replies")
                if replies:
                    for reply in replies:
                        body = reply.get("bodyHTML")
                        if body:
                            reply["bodyHTML"] = Markup(body)
        
        return pr_data

