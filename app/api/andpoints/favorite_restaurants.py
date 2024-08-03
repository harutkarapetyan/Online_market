
from fastapi import HTTPException, status, APIRouter, Query
from fastapi.responses import JSONResponse

import main

favorite_restaurants_router = APIRouter(tags=["favorite_restaurants"], prefix="/favorite_restaurants")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@favorite_restaurants_router.post("/add_favorite_restaurants")
def add_favorite_restaurants(user_id: int, restaurant_id: int):

    try:
        main.cursor.execute("""SELECT restaurant_id FROM favorite_restaurants WHERE
                                restaurant_id =%s AND user_id = %s""",
                            (restaurant_id, user_id))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        target = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    if target:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "The restaurant is already on your list"},
                            headers=headers)

    try:
        main.cursor.execute("""SELECT * FROM users WHERE user_id = %s """,
                            (user_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        user = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"User by {user_id} id not found"})

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s """,
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Restaurants by {user_id} id not found"})

    try:
        main.cursor.execute("""INSERT INTO favorite_restaurants (user_id, restaurant_id) 
                            VALUES (%s, %s)""",
                            (user_id, restaurant_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error adding favorite restaurant"
                                    f"ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully added"},
                        headers=headers)


@favorite_restaurants_router.delete("/delete_favorite_restaurant/{restaurant_id}")
def delete_favorite_restaurant(restaurant_id: int, user_id: int):
    try:
        main.cursor.execute("""SELECT * FROM favorite_restaurants WHERE restaurant_id =%s AND user_id =%s""",
                            (restaurant_id, user_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    try:
        restaurant = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Favorite restaurant by {restaurant_id} id not found"})

    try:
        main.cursor.execute("""DELETE FROM favorite_restaurants WHERE restaurant_id = %s AND user_id =%s""",
                            (restaurant_id, user_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"An error occurred while deleting, please try again"
                                    f"ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully deleted"},
                        headers=headers)


@favorite_restaurants_router.get("/get_all_favorite_restaurants_by_user_id/{user_id}")
def get_all_favorite_restaurants_by_user_id(user_id: int, page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM favorite_restaurants")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        count = main.cursor.fetchall()[0]['count']
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        main.cursor.execute("""SELECT user_id, restaurant_id 
                FROM favorite_restaurants WHERE user_id =%s LIMIT %s OFFSET %s""",
                            (user_id, per_page, offset))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        favorite_restaurants = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=
                            {f"An error occurred while searching for all favorite restaurants. ERROR {str(error)}"})

    if not favorite_restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"User with id {user_id} has no favorite restaurants"})

    restaurants_ids = [food.get("restaurant_id") for food in favorite_restaurants]

    data = {
        "page": page,
        "total_pages": max_page,
        "total_foods": count
    }

    content = {
        "restaurant_ids": restaurants_ids,
        "data": data
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)
