from fastapi import HTTPException, status, APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse

from models.models import User, Food, FavoriteFood
from database import get_db

favorite_foods_router = APIRouter(tags=["favorite_foods"], prefix="/favorite_foods")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@favorite_foods_router.post("/add_favorite_foods")
def add_favorite_foods(user_id: int, food_id: int, db: Session = Depends(get_db)):

    favorite_food = db.query(FavoriteFood).filter(FavoriteFood.food_id == food_id, FavoriteFood.user_id == user_id).first()
    if favorite_food:
        return JSONResponse(status_code=status.HTTP_200_OK,
                             content={"message": "The food is already on your list"},
                             headers=headers)

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"message": f"User with ID {user_id} not found"})

    # Check if the food exists
    food = db.query(Food).filter(Food.food_id == food_id).first()
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"message": f"Food with ID {food_id} not found"})


    try:
        new_favorite_food = FavoriteFood(user_id=user_id, food_id=food_id)
        db.add(new_favorite_food)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail={"message": f"There was an error adding favorite food. ERROR: {str(error)}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite food successfully added"},
                        headers=headers)


@favorite_foods_router.delete("/delete_favorite_food/{food_id}")
def delete_favorite_food(food_id: int, user_id: int, db: Session = Depends(get_db)):
    try:
        food = db.query(FavoriteFood).filter(FavoriteFood.food_id == food_id, FavoriteFood.user_id == user_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Favorite food with food_id {food_id} not found for user {user_id}"})

    try:
        db.delete(food)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"An error occurred while deleting, please try again. ERROR: {str(error)}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite food successfully deleted"},
                        headers=headers)


@favorite_foods_router.get("/get_all_favorite_foods_by_user_id/{user_id}")
def get_all_favorite_foods_by_user_id(user_id: int, page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    try:
        count = db.query(FavoriteFood).filter(FavoriteFood.user_id == user_id).count()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        favorite_foods = db.query(FavoriteFood.food_id).filter(FavoriteFood.user_id == user_id).limit(per_page).offset(offset).all()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    if not favorite_foods:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"User with id {user_id} has no favorite foods"})

    food_ids = [food[0] for food in favorite_foods]

    data = {
        "page": page,
        "total_pages": max_page,
        "total_foods": count
    }

    content = {
        "food_ids": food_ids,
        "data": data
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)