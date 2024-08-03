from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import main
import datetime

from schemas.shemas import UpdateRestaurant

restaurant_router = APIRouter(tags=["restaurant"], prefix="/restaurant")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@restaurant_router.post("/add_restaurant")
def add_restaurant(restaurant_name: str = Form(...), kind: str = Form(...), description: str = Form(...),
                   restaurant_email: str = Form(...), phone_number: str = Form(...),
                   address: str = Form(...), rating: float = Form(), image_logo: UploadFile = File(...),
                   image_background: UploadFile = File(...)):

    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:

        main.cursor.execute("""INSERT INTO restaurants (restaurant_name, kind, description, restaurant_email, phone_number,
                         address, rating, background_image, logo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (restaurant_name, kind, description, restaurant_email,
                             phone_number, address, rating, background_image_name,
                             logo_image_name))
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

        with open(f"{os.getcwd()}/static/images/logo/{logo_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_logo.file, file_object)

        with open(f"{os.getcwd()}/static/images/background/{background_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_background.file, file_object)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant successfully added"},
                        headers=headers)


@restaurant_router.put("/update_restaurant/{restaurant_id}")
def update_restaurant(restaurant_id: int, data: UpdateRestaurant):
    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id= %s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        target_restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Restaurant not found")

    try:
        main.cursor.execute("""UPDATE restaurants SET  restaurant_name=%s, restaurant_email=%s, 
                            phone_number=%s, rating=%s   
                            WHERE restaurant_id = %s""",
                            (data.restaurant_name, data.restaurant_email, data.phone_number,
                             data.rating, restaurant_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant updated successfully"},
                        headers=headers)


@restaurant_router.put("/update_logo_restaurants/{restaurant_id}")
def update_logo(restaurant_id, image_logo: UploadFile = File(...)):

    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        target_restaurant = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    old_image_logo = target_restaurant.get('logo')

    try:
        main.cursor.execute("""UPDATE restaurants SET logo = %s WHERE restaurant_id = %s""",
                            (logo_image_name, restaurant_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    logo_path = f"{os.getcwd()}/static/images/logo/"

    if old_image_logo and os.path.exists(os.path.join(logo_path, old_image_logo)):
        os.remove(os.path.join(logo_path, old_image_logo))

    with open(os.path.join(logo_path, logo_image_name), "wb") as file_object:
        shutil.copyfileobj(image_logo.file, file_object)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant logo updated successfully"},
                        headers=headers)


@restaurant_router.put("/update_background_restaurants/{restaurant_id}")
def update_background(restaurant_id, image_background: UploadFile = File(...)):
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        target_restaurant = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    old_image_background = target_restaurant.get('background_image')
    try:
        main.cursor.execute("""UPDATE restaurants SET  background_image = %s WHERE restaurant_id = %s""",
                            (background_image_name, restaurant_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    try:
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    background_path = f"{os.getcwd()}/static/images/background/"

    if old_image_background and os.path.exists(os.path.join(background_path, old_image_background)):
        os.remove(os.path.join(background_path, old_image_background))

    with open(os.path.join(background_path, background_image_name), "wb") as file_object:
        shutil.copyfileobj(image_background.file, file_object)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant background updated successfully"},
                        headers=headers)


@restaurant_router.delete("/delete_restaurant/{restaurant_id}")
def delete_restaurant(restaurant_id: int):
    try:
        main.cursor.execute("""SELECT logo, background_image FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:

        target_restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Restaurant not found")
    try:
        main.cursor.execute("""DELETE FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    try:
        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    logo_path = os.path.join(os.getcwd(), "static", "images", "logo", target_restaurant.get('logo', ''))
    background_path = os.path.join(os.getcwd(), "static", "images", "background",
                                       target_restaurant.get('background_image', ''))

    if os.path.exists(logo_path):
        os.remove(logo_path)

    if os.path.exists(background_path):
        os.remove(background_path)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant successfully deleted"},
                        headers=headers)


@restaurant_router.get("/get_restaurant_by_id/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int):
    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id=%s""",
                            (restaurant_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No restaurant found with {restaurant_id} id"
                                   f"ERROR: {error}")

    try:
        restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while searching for the restaurant"
                            f"ERROR: {error}")

    if restaurant is None:
        raise HTTPException(status_code=404,
                            detail=f"Restaurant with id {restaurant_id} was not found!")

    return JSONResponse(content=restaurant,
                        headers=headers)


@restaurant_router.get("/get_all_restaurants")
def get_all_restaurants(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
     main.cursor.execute("SELECT count(*) FROM restaurants")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        count = main.cursor.fetchone()['count']

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    if count == 0:
        return JSONResponse(content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        main.cursor.execute("SELECT * FROM restaurants LIMIT %s OFFSET %s",
                            (per_page, offset))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        restaurants = main.cursor.fetchall()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for all restaurants. ERROR: {str(error)}")

    if not restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Restaurants were not found!")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "restaurants": restaurants,
                            "page": page,
                            "total_pages": max_page,
                            "total_restaurants": count
                        }, headers=headers)


@restaurant_router.get("/get_logo/{logo_path}")
def get_image_logo(logo_path: str):
    path = f"{os.getcwd()}/static/images/logo/{logo_path}"
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(
        headers=headers,
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "File not found"
        }
    )


@restaurant_router.get("/get_background/{background_path}")
def get_image_background(background_path: str):
    path = f"{os.getcwd()}/static/images/background/{background_path}"
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(
        headers=headers,
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "File not found"
        }
    )


@restaurant_router.get("/get-all-foods-by-type/{restaurant_id}")
def get_all_foods_by_type(restaurant_id: int, food_kind: str, page: int = Query(default=1, ge=1)):
    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id=%s""",
                            (restaurant_id,))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"ERROR": {str(error)}})

    try:
        restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"ERROR": {str(error)}})

    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Restaurant by {restaurant_id} not found"})

    per_page = 20
    try:

        main.cursor.execute("SELECT count(*) FROM foods WHERE restaurant_id=%s AND kind=%s""",
                            (restaurant_id, food_kind))

        count = main.cursor.fetchone()['count']

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK,content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        main.cursor.execute("""SELECT * FROM foods WHERE restaurant_id=%s AND kind=%s LIMIT %s OFFSET %s""",
                            (restaurant_id, food_kind, per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"ERROR": {str(error)}})

    try:
        foods = main.cursor.fetchall()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for all foods by kind. ERROR: {str(error)}")

    if not foods:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Foods were not found!")

    food_ids = [food.get("food_id") for food in foods]

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

