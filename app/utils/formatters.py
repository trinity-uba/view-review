"""포매터 유틸리티"""

from datetime import datetime


def format_time(timestamp: str) -> str:
    """
    ISO 8601 시간을 사람이 읽기 쉬운 형태로 변환
    
    Args:
        timestamp: ISO 8601 형식의 타임스탬프 문자열
    
    Returns:
        포매팅된 시간 문자열 (예: "2시간 전", "3일 전")
    """
    if not timestamp:
        return ""
    
    try:
        # Z를 +00:00으로 변환하여 파싱
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years}년 전"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months}개월 전"
        elif diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    except (ValueError, AttributeError) as e:
        # 파싱 실패 시 원본의 날짜 부분만 반환
        try:
            return timestamp[:10]  # YYYY-MM-DD 형식
        except:
            return str(timestamp)

