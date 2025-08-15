from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current user from a token.
    This will be used to protect endpoints.
    """
    payload = verify_token(token) # Here is where your function gets used!
    
    mobile_number: str = payload.get("sub")
    if mobile_number is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        
    user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user