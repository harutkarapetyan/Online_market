from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from models.models import Food, Restaurant
from schemas.shemas import UpdateFood
import datetime
import os
import shutil
from database import get_db

food_router = APIRouter(tags=["food"], prefix="/api/food")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@food_router.post("/add_food/{restaurant_id}")
def add_food(
        restaurant_id: int,
        kind: str = Form(...),
        price: int = Form(...),
        cook_time: int = Form(...),
        food_name: str = Form(...),
        description: str = Form(...),
        rating: float = Form(...),
        image_food: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    food_image_name = f"food_image_{current_date_time}.{image_food.filename.split('.')[-1]}"

    new_food = Food(
        kind=kind,
        price=price,
        cook_time=cook_time,
        food_name=food_name,
        description=description,
        rating=rating,
        image=food_image_name,
        restaurant_id=restaurant_id,
    )

    try:
        db.add(new_food)
        db.commit()
        db.refresh(new_food)

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error occurred while saving food: {error}"
        )

    try:
        image_path = f"{os.getcwd()}/static/images/food/{food_image_name}"
        with open(image_path, "wb") as file_object:
            shutil.copyfileobj(image_food.file, file_object)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error occurred while saving the image: {error}"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Food successfully added"},
        headers=headers
    )

@food_router.put("/update_food/{food_id}")
def update_food(food_id: int, data: UpdateFood, db: Session = Depends(get_db)):
    target_food = db.query(Food).filter(Food.food_id == food_id).first()

    if target_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Food not found")

    try:
        target_food.kind = data.kind
        target_food.price = data.price
        target_food.cook_time = data.cook_time
        target_food.food_name = data.food_name
        target_food.description = data.description


        if data.rating is not None:
            target_food.rating = data.rating

        if data.restaurant_id is not None:
            target_food.restaurant_id = data.restaurant_id

        db.commit()
        db.refresh(target_food)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while updating food: {error}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Food updated successfully"},
        headers=headers
    )


@food_router.put("/update_images_foods/{food_id}")
def update_images(food_id: int, image_food: UploadFile = File(...), db: Session = Depends(get_db)):
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    food_image_name = f"food_image_{current_date_time}.{image_food.filename.split('.')[-1]}"

    target_food = db.query(Food).filter(Food.food_id == food_id).first()

    if target_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Food not found")


    old_image_path = target_food.image

    try:
        target_food.image = food_image_name
        db.commit()
        db.refresh(target_food)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while updating food image in database: {error}")

    try:

        if old_image_path and os.path.exists(f"{os.getcwd()}/static/images/food/{old_image_path}"):
            os.remove(f"{os.getcwd()}/static/images/food/{old_image_path}")

        with open(f"{os.getcwd()}/static/images/food/{food_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_food.file, file_object)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while saving the image: {error}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Food images updated successfully"},
        headers=headers
    )


@food_router.delete("/delete_food/{food_id}")
def delete_food(food_id: int, db: Session = Depends(get_db)):
    target_food = db.query(Food).filter(Food.food_id == food_id).first()

    if target_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Food not found")

    try:
        if target_food.image and os.path.exists(f"{os.getcwd()}/static/images/food/{target_food.image}"):
            os.remove(f"{os.getcwd()}/static/images/food/{target_food.image}")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while removing image: {error}")

    try:
        db.delete(target_food)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while deleting food: {error}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Food successfully deleted"},
                        headers=headers)



def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

@food_router.get("/get_food_by_id/{food_id}")
def get_food_by_id(food_id: int, db: Session = Depends(get_db)):
    try:
        food = db.query(Food).filter(Food.food_id == food_id).first()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for the food. ERROR: {error}")

    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Food with id {food_id} was not found!")

    return JSONResponse(content={"food": model_to_dict(food)}, headers=headers)


@food_router.get("/get_all_foods")
def get_all_foods(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        count = db.query(Food).count()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while counting foods. ERROR: {error}")

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        foods = db.query(Food).offset(offset).limit(per_page).all()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for foods. ERROR: {error}")

    if not foods:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Foods were not found!")

    content = {
        "foods": [model_to_dict(food) for food in foods],
        "page": page,
        "total_pages": max_page,
        "total_foods": count
    }

    return JSONResponse(content=content, headers=headers)




@food_router.get("/get_food_image/{food_id}")
def get_food_image(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Food).filter(Food.food_id == food_id).first()

    if not food or not food.image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food image not found"
        )

    file_name = food.image
    file_path = f"{os.getcwd()}/static/images/food/{file_name}"

    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )
