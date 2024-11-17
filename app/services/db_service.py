from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models.models import Base



def get_row(db: Session, model: Base, criteria: dict | None):
    try:
        query = db.query(model)

        if criteria:
            for key, value in criteria.items():
                query = query.filter(getattr(model, key) == value)

        return query.first()  # We only want to fetch one row

    except NoResultFound:
        return None



def add_row(db: Session, model: Base, data: dict):
    try:
        # Creating an instance of the model
        new_row = model(**data)
        db.add(new_row)
        db.commit()
        db.refresh(new_row)  # To get the new row with assigned values (e.g., auto-incremented ID)
        return new_row
    except Exception as e:
        db.rollback()  # In case of any error, rollback the transaction
        print(f"Error adding row: {e}")
        return None

