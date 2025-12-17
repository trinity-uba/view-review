"""캐싱 유틸리티"""

from functools import wraps
from typing import Callable, Any, Optional
import hashlib
import json
from flask import current_app
from flask_caching import Cache

# Flask-Caching 인스턴스
cache = Cache()


def init_cache(app) -> None:
    """
    캐시 초기화
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    # 간단한 메모리 캐시 사용 (프로덕션에서는 Redis 등 사용 권장)
    cache_config = {
        'CACHE_TYPE': 'simple',  # 'simple', 'redis', 'memcached' 등
        'CACHE_DEFAULT_TIMEOUT': 300,  # 기본 5분
    }
    
    # 환경 변수로 캐시 타입 설정 가능
    cache_type = app.config.get('CACHE_TYPE', 'simple')
    if cache_type == 'redis':
        cache_config.update({
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
        })
    elif cache_type == 'memcached':
        cache_config.update({
            'CACHE_TYPE': 'memcached',
            'CACHE_MEMCACHED_SERVERS': app.config.get('CACHE_MEMCACHED_SERVERS', ['127.0.0.1:11211']),
        })
    
    cache.init_app(app, config=cache_config)
    app.logger.info(f'캐시 시스템 초기화 완료: {cache_type}')


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    캐시 키 생성
    
    Args:
        prefix: 캐시 키 접두사
        *args: 위치 인자
        **kwargs: 키워드 인자
    
    Returns:
        생성된 캐시 키
    """
    # 인자를 정렬하여 일관된 키 생성
    key_data = json.dumps([args, sorted(kwargs.items())], sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cached(timeout: int = 300, key_prefix: Optional[str] = None):
    """
    캐싱 데코레이터
    
    Args:
        timeout: 캐시 만료 시간 (초)
        key_prefix: 캐시 키 접두사 (None이면 함수 이름 사용)
    
    사용 예시:
        @cached(timeout=60)
        def get_repo_info():
            # ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            prefix = key_prefix or f"{f.__module__}.{f.__name__}"
            key = cache_key(prefix, *args, **kwargs)
            
            # 캐시에서 조회
            result = cache.get(key)
            if result is not None:
                current_app.logger.debug(f"캐시 히트: {key}")
                return result
            
            # 캐시 미스: 함수 실행
            current_app.logger.debug(f"캐시 미스: {key}")
            result = f(*args, **kwargs)
            
            # 결과 캐싱
            cache.set(key, result, timeout=timeout)
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None) -> None:
    """
    캐시 삭제
    
    Args:
        pattern: 삭제할 캐시 키 패턴 (None이면 전체 삭제)
    """
    if pattern:
        # 패턴 기반 삭제 (구현은 캐시 타입에 따라 다름)
        current_app.logger.info(f"캐시 삭제: 패턴={pattern}")
        # Redis의 경우 keys() + delete() 사용
        # SimpleCache의 경우 전체 삭제만 가능
        cache.clear()
    else:
        current_app.logger.info("전체 캐시 삭제")
        cache.clear()

