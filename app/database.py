from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

# DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost/new_menu_am"
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/newmenuam"

engine = create_engine(DATABASE_URL,echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




def check_connection():
    while True:
        try:
            db = SessionLocal()
            # db.execute(text('SELECT 1'))
            print("Connection successfully")
            db.close()
            break
        except Exception as error:
            print(f"Connection failed: {error}")
            time.sleep(3)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


