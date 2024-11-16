from sqlalchemy.orm import Session
from sqlalchemy import text

import random
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from services.service_email import send_email
from core import security
from database import get_db
from models.models import User, ResetPassword
from services.db_service import get_row, add_row
from schemas.shemas import PasswordReset

forgot_router = APIRouter(tags=["Forgot password"], prefix="/password_reset")

sender = "niddleproject@gmail.com"
password = "ngzr kwsw jvcs oiae"


@forgot_router.post("/request/{email}")
def forgot_password(email: str, db: Session = Depends(get_db)):
    try:
        criteria = {"email": email}
        target_user = get_row(db, User, criteria)

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{email}' was not found!")

    try:
        code = random.randint(99999, 1000000)

        subject = "Password Reset E-mail"

        body = f"""You received this email because
                    you or someone else has requested a password reset for your user account at.

                    YOUR CODE
                    {code}

                    If you did not request a password reset you can safely ignore this email
                  """
        send_email(subject, body, sender, email, password)

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": "Mail service fail, please contact us",
                                    "detail": str(error)})

    try:
        reset_entry = ResetPassword(user_id=target_user.user_id, code=code)  # Create instance of RessetPassword model
        db.add(reset_entry)
        db.commit()
        db.refresh(reset_entry)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"detail": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "We sent you a personal CODE, please check your mail"})



@forgot_router.post('/reset')
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password does not match"
        )

    try:

        target_user = get_row(db, User, {"email": reset_data.email})

        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{reset_data.email}' was not found"
            )


        reset = get_row(db, ResetPassword, {"user_id": target_user.user_id})


        if reset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reset request not found"
            )

        if reset_data.code != reset.code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired reset code"
            )

        hashed_password = security.hash_password(reset_data.new_password)


        db.execute(
            text("UPDATE users SET password=:password WHERE email=:email"),
            {"password": hashed_password, "email": reset_data.email}
        )

        db.execute(
            text("DELETE FROM password_reset WHERE user_id = :user_id AND code = :code"),
            {"user_id": target_user.user_id, "code": reset_data.code}
        )

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Password changed successfully"}
        )

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "detail": str(error)}
        )
