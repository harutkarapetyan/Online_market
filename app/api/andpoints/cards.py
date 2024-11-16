from fastapi import HTTPException, status, Depends, APIRouter, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core import security
from schemas.shemas import AddCard
from models.models import Card
from database import get_db


card_router = APIRouter(tags=["cards"], prefix="/cards")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@card_router.post("/add-card")
def add_card(card_data: AddCard, db: Session = Depends(get_db), current_user = Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    new_card = Card(
        card_number=card_data.card_number,
        card_valid_thru=card_data.card_valid_thru,
        card_name=card_data.card_name,
        card_cvv=card_data.card_cvv,
        user_id=user_id
    )

    try:
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error adding the card. ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Card successfully added"},
                        headers=headers)



@card_router.delete("/delete-card-by-id/{card_id}")
def delete_card_by_id(card_id: int, db: Session = Depends(get_db), current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    card = db.query(Card).filter(Card.card_id == card_id).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Card with ID {card_id} not found.")

    if card.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to delete this card.")

    try:
        db.delete(card)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Successfully deleted"},
                            headers=headers)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error deleting card. ERROR: {error}"})



@card_router.get("/get-card-by-id/{card_id}")
def get_card_by_id(card_id: int,  db: Session = Depends(get_db), current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        card = db.query(Card).filter(Card.card_id == card_id).first()

        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Card with ID {card_id} not found.")

        if card.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You do not have permission to access this card.")

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={
                                "card_id": card.card_id,
                                "card_number": card.card_number,
                                "card_valid_thru": card.card_valid_thru,
                                "card_name": card.card_name,
                                "card_cvv": card.card_cvv,
                                "user_id": card.user_id
                            },
                            headers=headers)

    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error retrieving the card. ERROR: {error}"})



@card_router.get("/get-all-cards-by-user")
def get_all_cards_by_user(db: Session = Depends(get_db), current_user = Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    try:
        cards = db.query(Card).filter(Card.user_id == user_id).all()

        if not cards:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": "User doesn't have cards"})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[
                {
                    "card_id": card.card_id,
                    "card_number": card.card_number,
                    "card_valid_thru": card.card_valid_thru,
                    "card_name": card.card_name,
                    "card_cvv": card.card_cvv,
                    "status": card.status
                } for card in cards
            ],
            headers=headers
        )

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"There was an error getting cards. ERROR: {error}"}
        )



@card_router.put("/change-main-card/{card_id}")
def change_main_card(card_id: int, db: Session = Depends(get_db), current_user=Depends(security.get_current_user)):
    user_id = dict(current_user).get("user_id")

    card = db.query(Card).filter(Card.card_id == card_id).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found."
        )

    if card.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "You do not have permission to change this card."}
        )


    current_main_card = db.query(Card).filter(Card.user_id == user_id, Card.status == True).first()

    try:
        if current_main_card:

            current_main_card.status = False
            db.commit()

        card.status = True
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"{card_id} is now the main card"}
        )

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"There was an error updating the card status. ERROR: {error}"}
        )


