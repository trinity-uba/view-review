"""데이터베이스 모델 정의"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemy 인스턴스 생성 (app/__init__.py에서 초기화됨)
db = SQLAlchemy()


class CommentCheck(db.Model):
    """코멘트 체크 상태를 저장하는 모델
    
    각 PR의 코멘트에 대한 사용자의 대응 완료 여부를 저장합니다.
    """
    
    __tablename__ = 'comment_checks'
    
    # 기본 키
    id = db.Column(db.Integer, primary_key=True)
    
    # PR 및 코멘트 식별 정보
    pr_number = db.Column(db.Integer, nullable=False, index=True)
    comment_id = db.Column(db.String(100), nullable=False, index=True)
    
    # 저장소 정보 (PR이 속한 저장소)
    repo_owner = db.Column(db.String(200), nullable=False)
    repo_name = db.Column(db.String(200), nullable=False)
    
    # 체크 상태
    is_checked = db.Column(db.Boolean, default=True, nullable=False)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 복합 유니크 제약조건: 같은 PR의 같은 코멘트는 하나의 레코드만 존재
    __table_args__ = (
        db.UniqueConstraint('pr_number', 'comment_id', name='uq_pr_comment'),
    )
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'pr_number': self.pr_number,
            'comment_id': self.comment_id,
            'repo_owner': self.repo_owner,
            'repo_name': self.repo_name,
            'is_checked': self.is_checked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<CommentCheck(pr={self.pr_number}, comment={self.comment_id}, checked={self.is_checked})>"

