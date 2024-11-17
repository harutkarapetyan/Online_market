from fastapi import APIRouter, HTTPException, status, Depends, Form, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import datetime
import os
import shutil
from models.models import User  # Assuming the SQLAlchemy User model is in the models.py file
from core import security
from core.confirm_registration import mail_verification_email
from schemas.shemas import UserAdd, UserLogin
from database import get_db

auth_router = APIRouter(tags=["auth"], prefix="/api/auth")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@auth_router.get("/mail_verification/{email}")
def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    user.status = True
    db.commit()
    db.refresh(user)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "You have successfully passed the verification"},
                        headers=headers)


@auth_router.post("/add-user")
def add_user(name: str = Form(...), email: str = Form(...), password: str = Form(...),
             confirm_password: str = Form(...), phone_number: str = Form(...),
             profile_image: UploadFile = File(...), db: Session = Depends(get_db)):
    global profile_image_name
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

    if profile_image:
        profile_image_name = f"profile_image_{current_date_time}.{profile_image.filename.split('.')[-1]}"
    # else:
        # profile_image_name = f"default-avatar_{current_date_time}.png"

    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Incorrect password")

    user_hashed_password = security.hash_password(password)


    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists")

    # Insert user into database
    new_user = User(
        name=name,
        email=email,
        password=user_hashed_password,
        phone_number=phone_number,
        profile_image=profile_image_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Save profile image if provided
    if profile_image:
        try:
            with open(f"{os.getcwd()}/static/images/profile_image/{profile_image_name}", "wb") as file_object:
                shutil.copyfileobj(profile_image.file, file_object)
        except Exception as error:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={"message": error})

    # Send verification email
    mail_verification_email(email)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"message": "You have successfully registered"})



@auth_router.get("/get-one-user-by-id/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Error occurred while fetching user by id {user_id} ERROR: {error}')

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id {user_id} was not found!")

    # Return the user data as a JSON response
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"user_id": user.user_id, "name": user.name, "email": user.email,
                                 "phone_number": user.phone_number, "address": user.address,
                                 "profile_image": user.profile_image, "status": user.status},
                        headers=headers)



@auth_router.put("/update_profile_image/{user_id}")
def update_profile_image(user_id: int, profile_image: UploadFile = File(...), db: Session = Depends(get_db)):
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    profile_image_name = f"profile_image_{current_date_time}.{profile_image.filename.split('.')[-1]}"

    # Query to find the user by ID
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="User not found")

    old_image_path = target_user.profile_image

    try:
        target_user.profile_image = profile_image_name
        db.commit()


        if old_image_path and os.path.exists(f"{os.getcwd()}/static/images/profile_image/{old_image_path}"):
            os.remove(f"{os.getcwd()}/static/images/profile_image/{old_image_path}")

        with open(f"{os.getcwd()}/static/images/profile_image/{profile_image_name}", "wb") as file_object:
            shutil.copyfileobj(profile_image.file, file_object)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f"Error updating profile image: {str(error)}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Profile picture updated successfully"},
                        headers=headers)



@auth_router.get("/get_profile_image/{user_id}")
def get_profile_image(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user or not user.profile_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile image not found"
        )

    file_path = f"{os.getcwd()}/static/images/profile_image/{user.profile_image}"

    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )




@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db.delete(target_user)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})

    profile_image_path = os.path.join(os.getcwd(), "static", "images", "profile_image", target_user.profile_image)

    if os.path.exists(profile_image_path):
        os.remove(profile_image_path)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully deleted"}, headers=headers)



@auth_router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user_email = login_data.email

    user = db.query(User).filter(User.email == user_email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{user_email}' was not found!")

    if not user.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot log in because you have not completed authentication. Please check your email.")

    if not security.verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Wrong password")

    access_token = security.create_access_token({"user_id": user.user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Successfully logged in! Your access token",
                            "access_token": access_token,
                            "user_id": user.user_id
                        },
                        headers=headers)


@auth_router.get("/get_all_users")
def get_all_users(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    count = db.query(User).count()

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    users = db.query(User.user_id, User.name, User.email, User.phone_number, User.address, User.profile_image, User.status) \
              .limit(per_page) \
              .offset(offset) \
              .all()

    users_list = [
        {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "address": user.address,
            "profile_image": user.profile_image,
            "status": user.status,
        }
        for user in users
    ]

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "users": users_list,
                            "page": page,
                            "total_pages": max_page,
                            "total_users": count
                        },
                        headers=headers)
