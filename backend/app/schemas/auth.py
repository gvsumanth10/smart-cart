from pydantic import BaseModel, Field

# Schema for the user to request an OTP
class OTPRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Mobile number in E.164 format")

# Schema for the user to verify the OTP and log in
class OTPVerify(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Mobile number in E.164 format")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

# Schema for the token response after a successful login
class Token(BaseModel):
    access_token: str
    token_type: str