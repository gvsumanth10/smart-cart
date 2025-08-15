from fastapi import APIRouter, Depends, HTTPException, status, Request
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import random

from app.db.session import get_db
from app.schemas.auth import OTPRequest, OTPVerify, Token
from app.models.user import User, AuthOTPSession
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.limiter import limiter
from app.models.user import User

router = APIRouter()

@router.post("/send-otp", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
def request_otp(request: Request, otp_req: OTPRequest, db: Session = Depends(get_db)):
    """
    Generate and send an OTP to the user's mobile number.
    """
    mobile_number = otp_req.mobile_number
    # Check if the user exists
    # user = db.query(User).filter(User.mobile_number == mobile_number).first()
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # Generate a random 6-digit OTP
    otp_code = str(random.randint(100000,999999))  # Generate a random 6-digit OTP

    # Security: Hash the OTP before storing it
    hashed_otp = get_password_hash(otp_code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)  # OTP valid for 2 minutes

    # Store the hashed OTP Session in the Database
    otp_session = AuthOTPSession(
        mobile_number = mobile_number,
        hashed_otp = hashed_otp,
        expires_at = expires_at
    )
    db.add(otp_session)
    db.commit()

    # In a real application, you would send the OTP via SMS here
    # For this example, we will just return it in the response
    print(f"DEV-NOTE: OTP for {mobile_number} is {otp_code}")
    return {"message": "OTP sent successfully", "otp_code": otp_code}


@router.post("/verify-otp", response_model=Token)
def verify_otp(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify the OTP and return a JWT access token upon success.
    """
    now = datetime.now(timezone.utc)

    # Find the latest, unverified OTP for this number that has not expired
    otp_session = db.query(AuthOTPSession).filter(
        AuthOTPSession.mobile_number == otp_verify.mobile_number,
        AuthOTPSession.is_verified == False,
        AuthOTPSession.expires_at > now
    ).order_by(AuthOTPSession.created_at.desc()).first()

    # Security: Verify the OTP against the hashed OTP stored in the database
    if not otp_session or not verify_password(otp_verify.otp_code, otp_session.hashed_otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Mark the OTP as verified
    otp_session.is_verified = True
    db.commit()

    # Find User or create a new one if it doesn't exist
    user = db.query(User).filter(User.mobile_number == otp_verify.mobile_number).first()
    if not user:
        user = User(mobile_number=otp_verify.mobile_number)
        db.add(user)
        db.commit()
        db.refresh(user)
    # Create JWT access token and return it
    access_token = create_access_token(data={"sub": user.mobile_number}, expires_delta=timedelta(minutes=15))
    return Token(access_token=access_token, token_type="bearer")
    