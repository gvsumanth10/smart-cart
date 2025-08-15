from sqlalchemy import Column, Integer, String, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from app.db.base import Base
from datetime import datetime, timezone

# Base = declarative_base()

class User(Base):
    """
    User model for the application.
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique = True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
class AuthOTPSession(Base):
    """
    AuthOTPSession model for managing OTP sessions.
    """
    __tablename__ = 'auth_otp_sessions'
    session_id = Column(Integer, primary_key = True, index = True)
    mobile_number = Column(String, nullable = False, index = True)
    hashed_otp = Column(String, nullable = False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)