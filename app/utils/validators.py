"""입력 검증 유틸리티"""

from app.exceptions import ValidationError


def validate_pr_number(pr_number: int) -> int:
    """
    PR 번호 검증
    
    Args:
        pr_number: 검증할 PR 번호
    
    Returns:
        검증된 PR 번호
    
    Raises:
        ValidationError: PR 번호가 유효하지 않은 경우
    """
    if not isinstance(pr_number, int):
        raise ValidationError("PR 번호는 정수여야 합니다.", field="pr_number")
    
    if pr_number < 1:
        raise ValidationError("PR 번호는 1 이상의 정수여야 합니다.", field="pr_number")
    
    return pr_number


def validate_pr_state(state: str) -> str:
    """
    PR 상태 검증
    
    Args:
        state: 검증할 PR 상태
    
    Returns:
        검증된 PR 상태
    
    Raises:
        ValidationError: PR 상태가 유효하지 않은 경우
    """
    valid_states = ['open', 'closed', 'merged', 'all']
    
    if not isinstance(state, str):
        raise ValidationError("PR 상태는 문자열이어야 합니다.", field="state")
    
    state_lower = state.lower()
    if state_lower not in valid_states:
        raise ValidationError(
            f"PR 상태는 {', '.join(valid_states)} 중 하나여야 합니다. 받은 값: {state}",
            field="state"
        )
    
    return state_lower


def validate_pr_type(pr_type: str) -> str:
    """
    PR 타입 검증
    
    Args:
        pr_type: 검증할 PR 타입
    
    Returns:
        검증된 PR 타입
    
    Raises:
        ValidationError: PR 타입이 유효하지 않은 경우
    """
    valid_types = ['authored', 'reviewed']
    
    if not isinstance(pr_type, str):
        raise ValidationError("PR 타입은 문자열이어야 합니다.", field="type")
    
    pr_type_lower = pr_type.lower()
    if pr_type_lower not in valid_types:
        raise ValidationError(
            f"PR 타입은 {', '.join(valid_types)} 중 하나여야 합니다. 받은 값: {pr_type}",
            field="type"
        )
    
    return pr_type_lower


def validate_comment_body(body: str) -> str:
    """
    코멘트 본문 검증
    
    Args:
        body: 검증할 코멘트 본문
    
    Returns:
        검증된 코멘트 본문 (앞뒤 공백 제거)
    
    Raises:
        ValidationError: 코멘트 본문이 유효하지 않은 경우
    """
    if not isinstance(body, str):
        raise ValidationError("코멘트 본문은 문자열이어야 합니다.", field="body")
    
    body_stripped = body.strip()
    
    if not body_stripped:
        raise ValidationError("코멘트 본문은 비어있을 수 없습니다.", field="body")
    
    if len(body_stripped) > 65536:  # GitHub 코멘트 최대 길이
        raise ValidationError(
            f"코멘트 본문은 65536자 이하여야 합니다. 현재 길이: {len(body_stripped)}",
            field="body"
        )
    
    return body_stripped

