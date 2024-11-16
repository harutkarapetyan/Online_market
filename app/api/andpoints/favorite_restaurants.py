from fastapi import HTTPException, status, APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models.models import FavoriteRestaurant, User, Restaurant

favorite_restaurants_router = APIRouter(tags=["favorite_restaurants"], prefix="/favorite_restaurants")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}

@favorite_restaurants_router.post("/add_favorite_restaurants")
def add_favorite_restaurants(user_id: int, restaurant_id: int, db: Session = Depends(get_db)):
    existing_favorite = db.query(FavoriteRestaurant).filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if existing_favorite:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "The restaurant is already on your list"},
                            headers=headers)

    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User by {user_id} id not found")

    restaurant = db.query(Restaurant).filter_by(restaurant_id=restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Restaurant by {restaurant_id} id not found")

    new_favorite = FavoriteRestaurant(user_id=user_id, restaurant_id=restaurant_id)
    db.add(new_favorite)

    try:
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f"There was an error adding favorite restaurant: {error}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully added"},
                        headers=headers)

@favorite_restaurants_router.delete("/delete_favorite_restaurant/{restaurant_id}")
def delete_favorite_restaurant(restaurant_id: int, user_id: int, db: Session = Depends(get_db)):
    favorite_restaurant = db.query(FavoriteRestaurant).filter(
        FavoriteRestaurant.restaurant_id == restaurant_id,
        FavoriteRestaurant.user_id == user_id
    ).first()

    if not favorite_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Favorite restaurant with ID {restaurant_id} not found for user with ID {user_id}"
        )

    try:
        db.delete(favorite_restaurant)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the favorite restaurant. ERROR: {error}"
        )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully deleted"},
                        headers=headers)



@favorite_restaurants_router.get("/get_all_favorite_restaurants_by_user_id/{user_id}")
def get_all_favorite_restaurants_by_user_id(
        user_id: int,
        page: int = Query(default=1, ge=1),
        db: Session = Depends(get_db)
):
    per_page = 20

    count = db.query(FavoriteRestaurant).filter(FavoriteRestaurant.user_id == user_id).count()

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    favorite_restaurants = db.query(FavoriteRestaurant.restaurant_id).filter(FavoriteRestaurant.user_id == user_id) \
        .limit(per_page).offset(offset).all()

    if not favorite_restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} has no favorite restaurants")

    restaurant_ids = [restaurant_id[0] for restaurant_id in favorite_restaurants]

    data = {
        "page": page,
        "total_pages": max_page,
        "total_foods": count
    }

    content = {
        "restaurant_ids": restaurant_ids,
        "data": data
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)