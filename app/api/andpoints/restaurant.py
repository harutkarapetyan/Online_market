from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from enum import Enum
import os
import shutil
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas.shemas import UpdateRestaurant
from models.models import Restaurant, Food
from database import get_db

restaurant_router = APIRouter(tags=["restaurant"], prefix="/restaurant")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}

class RestaurantType(str, Enum):
    cafe = "cafe"
    bistro = "bistro"
    diner = "diner"
    sushi_restaurant = "sushi_restaurant"


@restaurant_router.post("/add_restaurant")
def add_restaurant(restaurant_name: str = Form(...), kind: RestaurantType = Form(...), description: str = Form(...),
                   restaurant_email: str = Form(...), phone_number: str = Form(...),
                   address: str = Form(...), rating: float = Form(), image_logo: UploadFile = File(...),
                   image_background: UploadFile = File(...), db: Session = Depends(get_db)):

    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:
        new_restaurant = Restaurant(
            restaurant_name=restaurant_name,
            kind=kind,
            description=description,
            restaurant_email=restaurant_email,
            phone_number=phone_number,
            address=address,
            rating=rating,
            logo=logo_image_name,
            background_image=background_image_name
        )
        db.add(new_restaurant)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        # Save images to disk
        with open(f"{os.getcwd()}/static/images/logo/{logo_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_logo.file, file_object)

        with open(f"{os.getcwd()}/static/images/background/{background_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_background.file, file_object)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant successfully added"},
                        headers=headers)

@restaurant_router.put("/update_restaurant/{restaurant_id}")
def update_restaurant(restaurant_id: int, data: UpdateRestaurant, db: Session = Depends(get_db)):
    target_restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Restaurant not found")

    try:
        target_restaurant.restaurant_name = data.restaurant_name
        target_restaurant.restaurant_email = data.restaurant_email
        target_restaurant.phone_number = data.phone_number
        target_restaurant.rating = data.rating

        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant updated successfully"},
                        headers=headers)


@restaurant_router.put("/update_logo_restaurants/{restaurant_id}")
def update_logo(restaurant_id: int, image_logo: UploadFile = File(...), db: Session = Depends(get_db)):

    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"

    try:
        target_restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    old_image_logo = target_restaurant.logo

    try:
        target_restaurant.logo = logo_image_name
        db.commit()

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    logo_path = f"{os.getcwd()}/static/images/logo/"

    if old_image_logo and os.path.exists(os.path.join(logo_path, old_image_logo)):
        os.remove(os.path.join(logo_path, old_image_logo))

    with open(os.path.join(logo_path, logo_image_name), "wb") as file_object:
        shutil.copyfileobj(image_logo.file, file_object)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant logo updated successfully"},
                        headers=headers)



@restaurant_router.put("/update_background_restaurants/{restaurant_id}")
def update_background(restaurant_id: int, image_background: UploadFile = File(...), db: Session = Depends(get_db)):

    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:
        target_restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    old_image_background = target_restaurant.background_image

    try:
        target_restaurant.background_image = background_image_name
        db.commit()

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    background_path = f"{os.getcwd()}/static/images/background/"

    if old_image_background and os.path.exists(os.path.join(background_path, old_image_background)):
        os.remove(os.path.join(background_path, old_image_background))

    with open(os.path.join(background_path, background_image_name), "wb") as file_object:
        shutil.copyfileobj(image_background.file, file_object)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant background updated successfully"},
                        headers=headers)


@restaurant_router.delete("/delete_restaurant/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):

    try:
        target_restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Restaurant not found")

    logo_path = os.path.join(os.getcwd(), "static", "images", "logo", target_restaurant.logo or '')
    background_path = os.path.join(os.getcwd(), "static", "images", "background", target_restaurant.background_image or '')

    if os.path.exists(logo_path):
        os.remove(logo_path)

    if os.path.exists(background_path):
        os.remove(background_path)

    try:
        db.delete(target_restaurant)
        db.commit()

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant successfully deleted"},
                        headers=headers)



def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

@restaurant_router.get("/get_restaurant_by_id/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int, db: Session = Depends(get_db)):
    try:
        restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for the restaurant. ERROR: {error}")

    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Restaurant with id {restaurant_id} was not found!")

    return JSONResponse(content={"restaurant": model_to_dict(restaurant)}, headers=headers)


@restaurant_router.get("/get_all_restaurants")
def get_all_restaurants(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20
    try:
        count = db.query(func.count(Restaurant.restaurant_id)).scalar()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if count == 0:
        return JSONResponse(content=[], headers=headers)

    max_page = (count - 1) // per_page + 1
    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        restaurants = db.query(Restaurant).limit(per_page).offset(offset).all()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if not restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Restaurants were not found!")

    restaurants_data = [model_to_dict(restaurant) for restaurant in restaurants]

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "restaurants": restaurants_data,
                            "page": page,
                            "total_pages": max_page,
                            "total_restaurants": count
                        }, headers=headers)


@restaurant_router.get("/get_logo/{restaurant_id}")
def get_logo_image(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    if not restaurant or not restaurant.logo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo image not found"
        )

    file_name = restaurant.logo
    file_path = f"{os.getcwd()}/static/images/logo/{file_name}"

    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )


@restaurant_router.get("/get_background/{restaurant_id}")
def get_background_image(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    if not restaurant or not restaurant.background_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Background image not found"
        )

    file_name = restaurant.background_image
    file_path = f"{os.getcwd()}/static/images/background/{file_name}"

    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )




@restaurant_router.get("/get-all-foods-by-type/{restaurant_id}")
def get_all_foods_by_type(
    restaurant_id: int,
    food_kind: str,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db)):
    per_page = 20


    restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Restaurant with ID {restaurant_id} not found"}
        )

    count = db.query(func.count(Food.food_id)).filter(
        Food.restaurant_id == restaurant_id, Food.kind == food_kind
    ).scalar()

    if count == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"food_ids": [], "data": {"page": 1, "total_pages": 0, "total_foods": 0}},
            headers=headers
        )


    max_page = (count - 1) // per_page + 1
    page = min(page, max_page)
    offset = (page - 1) * per_page

    foods = db.query(Food).filter(
        Food.restaurant_id == restaurant_id,
        Food.kind == food_kind
    ).offset(offset).limit(per_page).all()

    food_ids = [food.id for food in foods]


    content = {
        "food_ids": food_ids,
        "data": {
            "page": page,
            "total_pages": max_page,
            "total_foods": count
        }
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)
