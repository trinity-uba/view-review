"""애플리케이션 예외 클래스"""


class ViewReviewError(Exception):
    """기본 애플리케이션 에러"""
    pass


class GitHubAPIError(ViewReviewError):
    """GitHub API 관련 에러
    
    기존 github.api.GitHubAPIError와의 호환성을 유지하면서
    추가 기능(status_code)을 제공합니다.
    """
    
    def __init__(self, message: str, status_code: int = 500):
        """
        Args:
            message: 에러 메시지
            status_code: HTTP 상태 코드
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        """문자열 표현 (기존 코드 호환성)"""
        return self.message


class ValidationError(ViewReviewError):
    """입력 검증 에러"""
    
    def __init__(self, message: str, field: str = None):
        """
        Args:
            message: 에러 메시지
            field: 검증 실패한 필드명 (선택)
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


class NotFoundError(ViewReviewError):
    """리소스를 찾을 수 없을 때 발생하는 에러"""
    
    def __init__(self, resource_type: str, resource_id: str):
        """
        Args:
            resource_type: 리소스 타입 (예: "PR", "Comment")
            resource_id: 리소스 ID
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} #{resource_id}을(를) 찾을 수 없습니다."
        super().__init__(self.message)

