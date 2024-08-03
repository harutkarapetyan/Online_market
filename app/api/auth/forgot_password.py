from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import random

import main
from services.service_email import send_email
from schemas.shemas import PasswordReset
from services.db_service import get_row, add_row
from core import security

forgot_router = APIRouter(tags=["Forgot password"], prefix="/password_reset")

sender = "niddleproject@gmail.com"
password = "ngzr kwsw jvcs oiae"


@forgot_router.post("/request/{email}")
def forgot_password(email):
    try:
        target_user = get_row("users",
                              {"email": email})

    except Exception as error:
        main.conn.rollback()
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

                    If you did not request a password reset you can safely ignore this emai
                  """
        send_email(subject, body, sender, email, password)

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": "Mail service fail, please contact us",
                                    "detail": str(error)})

    try:
        add_row(table="password_reset",
                data={"user_id": target_user.get('user_id'),
                      "code": code})

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"detail": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "We sent you a personal CODE, please check your mail"})


@forgot_router.post('/reset')
def reset_password(reset_data: PasswordReset):
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="New password does not match")

    try:
        email = reset_data.email
        target_user = get_row("users",
                              {"email": email})

        if target_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with {email} was not found")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": "Something went wrong",
                                    "detail": str(error)})

    try:
        reset = get_row("password_reset",
                        {"user_id": target_user.get('user_id')})

        if reset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User by {email} has nor request, please request to change password")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": "Something went wrong",
                                    "detail": str(error)})

    if reset_data.code != reset.get("code"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Your CODE is invalid")

    try:
        hashed_password = security.hash_password(reset_data.new_password)
        main.cursor.execute("""UPDATE users SET password=%s WHERE email=%s""",
                            (hashed_password, email))

        main.conn.commit()

        main.cursor.execute("""DELETE FROM password_reset WHERE user_id = %s AND code = %s""",
                            (target_user.get('user_id'), reset_data.code))

        main.conn.commit()

        headers = {"Access-Control-Allow-Origin": "*",
                   "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                   "Access-Control-Allow-Headers": "Content-Type, Authorization",
                   "Access-Control-Allow-Credentials": "true"}

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Password changed successfully"},
                            headers=headers)

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": "Something went wrong",
                                    "detail": str(error)})
