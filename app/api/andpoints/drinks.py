from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from models.models import Drinks
from schemas.shemas import UpdateDrink
import datetime
import os
import shutil
from database import get_db

drink_router = APIRouter(tags=["drink"], prefix="/drink")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}

from enum import Enum

class Drink(str, Enum):
    carbonated = "carbonated"
    non_carbonated = "non_carbonated"
    to_alcohol = "to_alcohol"
    non_alcoholic = "non_alcoholic"


@drink_router.post("/add_drink/{restaurant_id}")
def add_drink(
    restaurant_id: int,
    kind: Drink = Form(...),
    price: int = Form(...),
    drink_name: str = Form(...),
    description: str = Form(...),
    rating: float = Form(...),
    image_drink: UploadFile = File(...),
    db: Session = Depends(get_db)):

    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    drink_image_name = f"drink_image_{current_date_time}.{image_drink.filename.split('.')[-1]}"
    image_directory = f"{os.getcwd()}/static/images/drink"

    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    new_drink = Drinks(
        kind=kind,
        price=price,
        drink_name=drink_name,
        description=description,
        rating=rating,
        image=drink_image_name,
        restaurant_id=restaurant_id
    )

    try:
        db.add(new_drink)
        db.commit()
        db.refresh(new_drink)

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Database error: {error}"}
        )

    try:
        with open(f"{image_directory}/{drink_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_drink.file, file_object)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error saving image: {error}"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Drink successfully added"},
        headers=headers
    )


@drink_router.put("/update_drink/{drink_id}")
def update_drink(drink_id: int, data: UpdateDrink, db: Session = Depends(get_db)):
    target_drink = db.query(Drinks).filter(Drinks.drink_id == drink_id).first()

    if target_drink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drink not found")


    target_drink.kind = data.kind
    target_drink.price = data.price
    target_drink.drink_name = data.drink_name
    target_drink.description = data.description
    target_drink.restaurant_id = data.restaurant_id

    try:
        db.commit()
        db.refresh(target_drink)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": f"Database error: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Drink updated successfully"}, headers=headers)



@drink_router.put("/update_images_drinks/{drink_id}")
def update_images(drink_id: int, image_drink: UploadFile = File(...), db: Session = Depends(get_db)):
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    drink_image_name = f"drink_image_{current_date_time}.{image_drink.filename.split('.')[-1]}"

    # Fetch the drink from the database
    target_drink = db.query(Drinks).filter(Drinks.drink_id == drink_id).first()

    if target_drink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Drink not found")

    old_image_path = target_drink.image

    target_drink.image = drink_image_name
    db.commit()

    try:

        if old_image_path and os.path.exists(f"{os.getcwd()}/static/images/drink/{old_image_path}"):
            os.remove(f"{os.getcwd()}/static/images/drink/{old_image_path}")

        with open(f"{os.getcwd()}/static/images/drink/{drink_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_drink.file, file_object)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Drink image updated successfully"},
                        headers=headers)


@drink_router.delete("/delete-drink/{drink_id}")
def delete_drink(drink_id: int, db: Session = Depends(get_db)):
    target_drink = db.query(Drinks).filter(Drinks.drink_id == drink_id).first()

    if not target_drink:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Drink not found"}
        )

    try:
        db.delete(target_drink)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(error)}
        )

    drink_image_path = os.path.join(
        os.getcwd(), "static", "images", "drink", target_drink.image or ""
    )

    if os.path.exists(drink_image_path):
        os.remove(drink_image_path)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Drink successfully deleted"},
        headers=headers
    )


def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

@drink_router.get("/get_drink_by_id/{drink_id}")
def get_drink_by_id(drink_id: int, db: Session = Depends(get_db)):
    try:
        drink = db.query(Drinks).filter(Drinks.drink_id == drink_id).first()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while searching for the drink. ERROR: {error}"
        )

    if drink is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} was not found!"
        )

    return JSONResponse(
        content={"drink": model_to_dict(drink)},
        headers=headers
    )



@drink_router.get("/get_all_drinks")
def get_all_drinks(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        count = db.query(Drinks).count()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while counting drinks. ERROR: {error}"}
        )

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1
    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        drinks = db.query(Drinks).limit(per_page).offset(offset).all()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while fetching drinks. ERROR: {error}"}
        )

    if not drinks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drinks were not found!"
        )


    drinks_list = [model_to_dict(drink) for drink in drinks]

    content = {
        "drinks": drinks_list,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)


@drink_router.get("/get_all_carbonated_drinks")
def get_all_carbonated_drinks(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        count = db.query(Drinks).filter(Drinks.kind == 'carbonated').count()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while counting carbonated drinks. ERROR: {error}"}
        )

    if count == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"drinks": [], "page": 1, "total_pages": 0, "total_drinks": 0},
            headers=headers,
        )

    max_page = (count - 1) // per_page + 1
    page = min(max(page, 1), max_page)

    offset = (page - 1) * per_page

    try:
        # Fetch the drinks
        drinks = db.query(Drinks).filter(Drinks.kind == 'carbonated').offset(offset).limit(per_page).all()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while fetching carbonated drinks. ERROR: {error}"}
        )

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No carbonated drinks found!")

    # Convert results to dictionary format
    content = {
        "drinks": [model_to_dict(drink) for drink in drinks],
        "page": page,
        "total_pages": max_page,
        "total_drinks": count,
    }

    return JSONResponse(content=content, headers=headers)




@drink_router.get("/get_all_non_carbonated_drinks")
def get_all_non_carbonated_drinks(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        # Count the total number of non-carbonated drinks
        count = db.query(Drinks).filter(Drinks.kind == 'non_carbonated').count()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while counting non-carbonated drinks. ERROR: {error}"}
        )

    max_page = (count - 1) // per_page + 1
    page = min(page, max_page)  # Adjust the page to avoid invalid offsets

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"drinks": [], "page": page, "total_pages": max_page, "total_drinks": count})

    offset = (page - 1) * per_page

    try:
        # Fetch non-carbonated drinks with pagination
        drinks = db.query(Drinks).filter(Drinks.kind == 'non_carbonated') \
            .offset(offset).limit(per_page).all()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while fetching non-carbonated drinks. ERROR: {error}"}
        )

    if not drinks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No non-carbonated drinks found!"
        )

    # Convert the drinks data to a dictionary format
    drinks_data = [model_to_dict(drink) for drink in drinks]

    content = {
        "drinks": drinks_data,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)


@drink_router.get("/get_all_to_alcohol_drinks")
def get_all_to_alcohol_drinks(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        # Count the total number of to_alcohol drinks
        count = db.query(Drinks).filter(Drinks.kind == 'to_alcohol').count()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while counting to_alcohol drinks. ERROR: {error}"}
        )

    max_page = (count - 1) // per_page + 1
    page = min(page, max_page)  # Adjust the page to avoid invalid offsets

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"drinks": [], "page": page, "total_pages": max_page, "total_drinks": count})

    offset = (page - 1) * per_page

    try:
        # Fetch to_alcohol drinks with pagination
        drinks = db.query(Drinks).filter(Drinks.kind == 'to_alcohol') \
            .offset(offset).limit(per_page).all()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while fetching to_alcohol drinks. ERROR: {error}"}
        )

    if not drinks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No to_alcohol drinks found!"
        )

    drinks_data = [model_to_dict(drink) for drink in drinks]

    content = {
        "drinks": drinks_data,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)



@drink_router.get("/get_all_non_alcoholic_drinks")
def get_all_non_alcoholic_drinks(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        count = db.query(Drinks).filter(Drinks.kind == 'non_alcoholic').count()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while counting non_alcoholic drinks. ERROR: {error}"}
        )

    max_page = (count - 1) // per_page + 1
    page = min(page, max_page)

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"drinks": [], "page": page, "total_pages": max_page, "total_drinks": count})

    offset = (page - 1) * per_page

    try:
        drinks = db.query(Drinks).filter(Drinks.kind == 'non_alcoholic') \
            .offset(offset).limit(per_page).all()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"An error occurred while fetching non_alcoholic drinks. ERROR: {error}"}
        )

    if not drinks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No non_alcoholic drinks found!"
        )

    drinks_data = [model_to_dict(drink) for drink in drinks]

    content = {
        "drinks": drinks_data,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)



@drink_router.get("/get_image/{drink_id}")
def get_drink_image(drink_id: int, db: Session = Depends(get_db)):
    drink = db.query(Drinks).filter(Drinks.drink_id == drink_id).first()

    if not drink:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drink not found"
        )

    image_file = drink.image
    path = os.path.join(os.getcwd(), "static/images/drink", image_file)

    if os.path.exists(path):
        return FileResponse(path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )