from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.db.base import Base
from datetime import datetime, timezone

class AuthOTPSession(Base):
    """
    Model for storing OTP sessions for user authentication.
    """
    __tablename__ = 'auth_otp_sessions'
    session_id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index= True, nullable=False)
    otp_code = Column(String, nullable = False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    