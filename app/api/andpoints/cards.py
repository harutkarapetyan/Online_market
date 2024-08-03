from fastapi import HTTPException, status, Depends, APIRouter, Query
from fastapi.responses import JSONResponse

import main

from core import security

from schemas.shemas import AddCard

card_router = APIRouter(tags=["cards"], prefix="/cards")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@card_router.post("/add-card")
def add_card(card_data: AddCard, current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        main.cursor.execute("""INSERT INTO cards (card_number, card_valid_thru, card_name, card_cvv, user_id)
            VALUES (%s, %s, %s, %s, %s)""",
                            (card_data.card_number, card_data.card_valid_thru, card_data.card_name,
                             card_data.card_cvv, user_id))
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error adding card"
                                               f"ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "card successfully added"},
                        headers=headers)


@card_router.delete("/delete-card-by-id/{card_id}")
def delete_card_by_id(card_id: int, current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        main.cursor.execute("SELECT user_id FROM cards WHERE card_id=%s",
                            (card_id,))

        user_id_checked = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting user_id"
                                               f"ERROR: {error}"})

    if user_id_checked is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Card with ID {card_id} not found.")

    if user_id_checked == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"message": "You do not have permission to delete this card."})

    try:
        main.cursor.execute("DELETE FROM cards WHERE card_id=%s", (card_id,))

        main.conn.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Successfully deleted"},
                            headers=headers)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error deleting card"
                                               f"ERROR: {error}"})


@card_router.get("/get-card-by-id/{card_id}")
def get_card_by_id(card_id: int, current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        main.cursor.execute("SELECT user_id FROM cards WHERE card_id=%s",
                            (card_id,))

        user_id_checked = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting user_id"
                                               f"ERROR: {error}"})

    if user_id_checked == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"message": "You do not have permission to get this card."})

    try:
        main.cursor.execute("""SELECT * FROM cards WHERE card_id=%s""",
                            (card_id,))

        card = main.cursor.fetchone()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=card,
                            headers=headers)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting card"
                                               f"ERROR: {error}"})


@card_router.get("/get-all-cards-by-user")
def get_all_cards_by_user(current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        main.cursor.execute("""SELECT * FROM cards WHERE user_id=%s""",
                            (user_id,))

        cards = main.cursor.fetchall()

        if cards is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": "User doesn't have cards"})

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=cards,
                            headers=headers)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting cards"
                                               f"ERROR: {error}"})


@card_router.put("/change-main-card/{card_id}")
def change_main_card(card_id: int, current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        main.cursor.execute("SELECT user_id FROM cards WHERE card_id=%s", (card_id,))
        result = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting user_id. ERROR: {error}"})

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Card with ID {card_id} not found.")

    user_id_checked = result['user_id']

    if user_id_checked != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"message": "You do not have permission to change this card."})

    try:
        main.cursor.execute("SELECT card_id FROM cards WHERE user_id=%s AND status=%s", (user_id, True))
        result = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error getting the current main card. ERROR: {error}"})

    card_id_old = result['card_id'] if result else None

    if card_id_old is None:
        try:
            main.cursor.execute("UPDATE cards SET status = %s WHERE card_id = %s", (True, card_id))
            main.conn.commit()
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"{card_id} is now the main card"})

        except Exception as error:
            main.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={
                                    "message": f"There was an error updating the status of {card_id}. ERROR: {error}"})

    try:
        main.cursor.execute("UPDATE cards SET status = %s WHERE card_id = %s", (False, card_id_old))
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={
                                "message": f"There was an error updating the status of the old main card {card_id_old}. ERROR: {error}"})

    try:
        main.cursor.execute("UPDATE cards SET status = %s WHERE card_id = %s", (True, card_id))
        main.conn.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"the main map was successfully changed"})

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error updating the status of {card_id}. ERROR: {error}"})
