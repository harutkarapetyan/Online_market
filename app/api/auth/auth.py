# Standard libs
import datetime


# FastAPI
from fastapi import HTTPException, status, Depends, APIRouter, Query, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import main
import shutil
import os
from core.confirm_registration import mail_verification_email

from core import security

from schemas.shemas import UserAdd, UserLogin


auth_router = APIRouter(tags=["auth"], prefix="/auth")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@auth_router.get("/mail_verification/{email}")
def verify_email(email: str):
    try:
        main.cursor.execute("""SELECT email FROM users WHERE email=%s""",
                            (email,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                       detail={"message": f"There was a error looking up the user in the authentication pool\n{error}"})

    email_checked = main.cursor.fetchone()

    if email_checked is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "User not found"})
    try:

        main.cursor.execute("""UPDATE users SET status=%s WHERE email=%s""",
                            (True, email))

        main.conn.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"An error occurred while updating user data\n{error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "You have successfully passed the verification"},
                        headers=headers)


@auth_router.post("/add-user")
def add_user(name: str = Form(...), email: str = Form(...), password: str = Form(...),
             confirm_password: str = Form(...), phone_number: str = Form(...),
             profile_image: UploadFile = File(...)): # Changed here

    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

    # Setting default profile image if none is provided
    if profile_image:
        profile_image_name = f"profile_image_{current_date_time}.{profile_image.filename.split('.')[-1]}"
    # else:
    #     profile_image_name = f"default-avatar_{current_date_time}.{profile_image.filename.split('.')[-1]}"

    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Incorrect password")

    user_password = password
    user_hashed_password = security.hash_password(user_password)

    # Check if email already exists
    try:
        main.cursor.execute(
            "SELECT email FROM users WHERE email = %s",
            (email,))
        check_email = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if check_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists")

    # Insert user into database
    try:
        main.cursor.execute("""INSERT INTO users (name, email, password, phone_number, profile_image)
                            VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                            (name, email, user_hashed_password, phone_number, profile_image_name))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error}
        )

    # Commit transaction
    try:
        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    # Save profile image if provided
    if profile_image:
        try:
            with open(f"{os.getcwd()}/static/images/profile_image/{profile_image_name}", "wb") as file_object:
                shutil.copyfileobj(profile_image.file, file_object)
        except Exception as error:
            main.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={"message": error})

    # Fetch created user
    try:
        user = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error in user-add fetch!\n"
                                   f"ERR: {error}")

    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="User not created")

    mail_verification_email(email)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"message": "You have successfully registered"})



@auth_router.get("/get-one-user-by-id/{user_id}")
def get_user_by_id(user_id: int):
    # current_user=Depends(security.get_current_user)
    try:
        main.cursor.execute("""SELECT user_id, name, email, phone_number, address, profile_image, status
                   FROM users WHERE user_id=%s""",
                            (user_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error occurred while trying to select user "
                                   f"by id {user_id}\n"
                                   f"ERROR: {error}")

    try:
        user = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error occurred while trying to fetch selected user "
                                   f"by id {user_id}\n"
                                   f"ERROR: {error}")

    if user is None:
        raise HTTPException(status_code=404,
                            detail=f"User with id {user_id} was not found!")

    return JSONResponse(status_code=status.HTTP_200_OK, content=user,
                        headers=headers)

@auth_router.put("/update_profile_image/{user_id}")
def update_profile_image(user_id: int,
                  profile_image: UploadFile = File(...)):
    # current_user = Depends(security.get_current_user)
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    profile_image_name = f"profile_image_{current_date_time}.{profile_image.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM users WHERE user_id= %s""", (user_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                            detail={"message": error})
    try:
        target_user = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    old_image_path = target_user.get('profile_image')

    try:

        main.cursor.execute("""UPDATE users SET profile_image = %s WHERE user_id = %s""",
                            (profile_image_name, user_id))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    try:

        if old_image_path and os.path.exists(f"{os.getcwd()}/static/images/profile_image/{old_image_path}"):
            os.remove(f"{os.getcwd()}/static/images/profile_image/{old_image_path}")

        with open(f"{os.getcwd()}/static/images/profile_image/{profile_image_name}", "wb") as file_object:
            shutil.copyfileobj(profile_image.file, file_object)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Profile picture updated successfully"},
                        headers=headers)



@auth_router.get("/get_profile_image/{file}")
def get_profile_image(file: str):
    path = f"{os.getcwd()}/static/images/profile_image/{file}"
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(
        headers=headers,
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "File not found"
        }
    )



@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int):
    # current_user=Depends(security.get_current_user)

    main.cursor.execute("""SELECT * FROM users WHERE user_id=%s""",
                            (user_id,))
    target_user = main.cursor.fetchone()
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "user not found"})
    try:
        main.cursor.execute("""DELETE FROM users WHERE user_id=%s""",
                            (user_id,))
        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    profile_image_path = os.path.join(os.getcwd(), "static", "images", "profile_image", target_user.get('profile_image', ''))

    if os.path.exists(profile_image_path):
        os.remove(profile_image_path)



    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Successfully deleted"},
                        headers=headers)



@auth_router.post("/login")
def login(login_data: UserLogin):
    user_email = login_data.email
    try:
        main.cursor.execute("""SELECT * FROM users WHERE email=%s""",
                            (user_email,))
        user = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{user_email}' was not found!")

    user = dict(user)
    if not user.get("status"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"message": """You cannot log in because you have not completed authentication. Please check your email."""})

    user_hashed_password = user.get("password")

    if not security.verify_password(login_data.password, user_hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Wrong password")

    user_id = user.get("user_id")
    access_token = security.create_access_token({"user_id": user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Successfully logged in! Your access token",
                            "access_token": access_token,
                            "user_id": user_id
                        },
                        headers=headers)


@auth_router.get("/get_all_users")
def get_all_users(page: int = Query(default=1, ge=1)):
    per_page = 20

    main.cursor.execute("SELECT count(*) FROM users")
    count = main.cursor.fetchall()[0]['count']
    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[],
                            headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:

        main.cursor.execute("""
                   SELECT user_id, name, email, phone_number, address, profile_image, status 
                   FROM users LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:

        users = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for all users. ERROR: {str(error)}")

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Users were not found!")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                                "users": users,
                                "page": page,
                                "total_pages": max_page,
                                "total_users": count
                                },
                        headers=headers)

