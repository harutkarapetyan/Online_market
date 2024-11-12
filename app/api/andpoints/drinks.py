from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
import datetime
import os
import shutil
import main
from enum import Enum

from schemas.shemas import UpdateDrink

drink_router = APIRouter(tags=["drink"], prefix="/drink")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}

class Drink(str, Enum):
    carbonated = "carbonated"
    non_carbonated = "non_carbonated"
    to_alcohol = "to_alcohol"
    non_alcoholic = "non_alcoholic"



@drink_router.post("/add_drink/{restaurant_id}")
def add_drink(restaurant_id: int, kind: Drink = Form(...), price: int = Form(...),
              drink_name: str = Form(...), description: str = Form(...), rating: float = Form(...),
              image_drink: UploadFile = File(...)):
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    drink_image_name = f"drink_image_{current_date_time}.{image_drink.filename.split('.')[-1]}"
    image_directory = f"{os.getcwd()}/static/images/drink"

    # Ensure the directory exists
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    try:
        main.cursor.execute("""INSERT INTO drinks (kind, price,
                        image, drink_name, description, rating, restaurant_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (kind, price, drink_image_name,
                             drink_name, description, rating, restaurant_id))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

    try:
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

    try:
        # Save the image file to the directory
        with open(f"{image_directory}/{drink_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_drink.file, file_object)

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Drink successfully added"},
                        headers=headers)


@drink_router.put("/update_drink/{drink_id}")
def update_drink(drink_id: int, data: UpdateDrink):
    try:
        main.cursor.execute("""SELECT * FROM drinks WHERE drink_id= %s""",
                            (drink_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    target_drink = main.cursor.fetchone()

    if target_drink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Drink not found")

    try:
        main.cursor.execute("""UPDATE drinks SET kind=%s, price=%s, 
                            cook_time=%s, drink_name=%s, description=%s  
                            WHERE drink_id = %s""",
                            (data.kind, data.price, data.cook_time,
                             data.drink_name, data.description, drink_id))
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
                        content={"message": "Drink updated successfully"},
                        headers=headers)

@drink_router.put("/update_images_drinks/{drink_id}")
def update_images(drink_id, image_drink: UploadFile = File(...)):
    current_date_time = (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    drink_image_name = f"drink_image_{current_date_time}.{image_drink.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM drinks WHERE drink_id= %s""", (drink_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
    try:
        target_drink = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if target_drink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Drink not found")

    old_image_path = target_drink.get('image')

    try:
        main.cursor.execute("""UPDATE drinks SET image = %s WHERE drink_id = %s""",
                            (drink_image_name, drink_id))

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
        if old_image_path and os.path.exists(f"{os.getcwd()}/static/images/drink/{old_image_path}"):
            os.remove(f"{os.getcwd()}/static/images/drink/{old_image_path}")

        with open(f"{os.getcwd()}/static/images/drink/{drink_image_name}", "wb") as file_object:
            shutil.copyfileobj(image_drink.file, file_object)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Drink images updated successfully"},
                        headers=headers)



@drink_router.delete("/delete-drink/{drink_id}")
def delete_drink(drink_id: int):
    main.cursor.execute("""SELECT * FROM drinks WHERE drink_id=%s""", (drink_id,))
    target_drink = main.cursor.fetchone()

    if target_drink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "drink not found"})

    try:
        main.cursor.execute("""DELETE FROM drinks WHERE drink_id=%s""", (drink_id,))
        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    drink_image_path = os.path.join(os.getcwd(), "static", "images", "drink", target_drink.get('image', ''))

    if os.path.exists(drink_image_path):
        os.remove(drink_image_path)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Successfully deleted"},
                        headers=headers)


@drink_router.get("/get_drink_by_id/{drink_id}")
def get_drink_by_id(drink_id: int):
    try:
        main.cursor.execute("""SELECT * FROM drinks WHERE drink_id=%s""",
                            (drink_id,))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No drink found with {drink_id} id"
                                   f"ERROR: {error}")

    try:
        drink = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while searching for the drink"
                            f"ERROR: {error}")

    if drink is None:
        raise HTTPException(status_code=404,
                            detail=f"Drink with id {drink_id} was not found!")

    return JSONResponse(status_code=status.HTTP_200_OK, content=drink, headers=headers)



@drink_router.get("/get_all_drinks")
def get_all_drinks(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM drinks")

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
        main.cursor.execute(f"""SELECT * FROM drinks LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        drinks = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for all drinks. ERROR: {str(error)}")

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Drinks were not found!")

    content = {
        "drinks": drinks,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)


@drink_router.get("/get_all_carbonated_drinks")
def get_all_carbonated_drinks(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM drinks WHERE kind = 'carbonated'")

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
        main.cursor.execute(f"""SELECT * FROM drinks WHERE kind = 'carbonated' LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        drinks = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for carbonated drinks. ERROR: {str(error)}")

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No carbonated drinks found!")

    content = {
        "drinks": drinks,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)


@drink_router.get("/get_all_non_carbonated_drinks")
def get_all_non_carbonated_drinks(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM drinks WHERE kind = 'non_carbonated'")

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
        main.cursor.execute(f"""SELECT * FROM drinks WHERE kind = 'non_carbonated' LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        drinks = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for non_carbonated drinks. ERROR: {str(error)}")

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No non_carbonated drinks found!")

    content = {
        "drinks": drinks,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)



@drink_router.get("/get_all_to_alcohol_drinks")
def get_all_to_alcohol_drinks(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM drinks WHERE kind = 'to_alcohol'")

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
        main.cursor.execute(f"""SELECT * FROM drinks WHERE kind = 'to_alcohol' LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        drinks = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for to_alcohol drinks. ERROR: {str(error)}")

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No to_alcohol drinks found!")

    content = {
        "drinks": drinks,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)



@drink_router.get("/get_all_non_alcoholic_drinks")
def get_all_non_alcoholic_drinks(page: int = Query(default=1, ge=1)):
    per_page = 20
    try:
        main.cursor.execute("SELECT count(*) FROM drinks WHERE kind = 'non_alcoholic'")

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
        main.cursor.execute(f"""SELECT * FROM drinks WHERE kind = 'non_alcoholic' LIMIT %s OFFSET %s""", (per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        drinks = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while searching for non_alcoholic drinks. ERROR: {str(error)}")

    if not drinks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No non_alcoholic drinks found!")

    content = {
        "drinks": drinks,
        "page": page,
        "total_pages": max_page,
        "total_drinks": count
    }

    return JSONResponse(content=content, headers=headers)


@drink_router.get("/get_image/{file}")
def get_drink_image(file: str):
    path = f"{os.getcwd()}/static/images/drink/{file}"
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(
        headers=headers,
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "File not found"
        }
    )
