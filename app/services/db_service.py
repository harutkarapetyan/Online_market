# import main
#
#
# def get_row(table: str, criteria: dict | None):
#     query = f"SELECT * FROM {table} WHERE"
#
#     if criteria != {}:
#         criteria_keys = criteria.keys()
#
#         i = 1
#         for key in criteria_keys:
#             if i > 1:
#                 query += ","
#             query += f" {key} = %s"
#             i += 1
#
#     main.cursor.execute(query, tuple(criteria.values()))
#
#     return main.cursor.fetchone()
#
#
# def add_row(table: str, data: dict):
#     query = f"INSERT INTO {table} "
#
#     data_keys = data.keys()
#     data_values = data.values()
#
#     query += "("
#     i = 1
#     for key in data_keys:
#         if i > 1:
#             query += ","
#         query += f" {key}"
#         i += 1
#
#     query += ") values ("
#
#     j = 1
#     for _ in data_values:
#         if j > 1:
#             query += ","
#         query += " %s"
#         j += 1
#
#     query += ") RETURNING *"
#
#     main.cursor.execute(query, tuple(data.values()))
#
#     return main.conn.commit()


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

