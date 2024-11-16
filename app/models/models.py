from sqlalchemy import Column, Integer, String, ForeignKey, text, Float, Boolean, TEXT
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base


# class User(Base):
#     __tablename__ = "users"
#
#     user_id = Column(Integer, nullable=False, primary_key=True)
#     name = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False, unique=True)
#     password = Column(String(255), nullable=False)
#     phone_number = Column(String(255), nullable=False)
#     address = Column(String(255), nullable=True)
#     profile_image = Column(String(255), nullable=True)
#     status = Column(Boolean, nullable=True, server_default="False")
#     created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    profile_image = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=True, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False,
        server_default=text("CURRENT_TIMESTAMP"))


# class Card(Base):
#     __tablename__ = "cards"
#
#     card_id = Column(Integer, nullable=False, primary_key=True)
#     card_number = Column(Integer, nullable=False)
#     card_valid_thru = Column(String(255), nullable=False)  # "MM/YYYY"
#     card_name = Column(String(255), nullable=False)
#     card_cvv = Column(Integer, nullable=False)
#     status = Column(Boolean, nullable=False, server_default="False") #main_card
#     user_id = Column(Integer, ForeignKey("users.user_id"))

class Card(Base):
    __tablename__ = "cards"

    card_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    card_number = Column(Integer, nullable=False)
    card_valid_thru = Column(String(255), nullable=False)
    card_name = Column(String(255), nullable=False)
    card_cvv = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False, server_default=text("0"))
    user_id = Column(Integer, ForeignKey("users.user_id"))


# class Order(Base):
#     __tablename__ = "orders"
#
#     order_id = Column(Integer, nullable=False, primary_key=True)
#     address_to = Column(String(255), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     food_id = Column(Integer, ForeignKey("foods.food_id"))
#     drink_id = Column(Integer, ForeignKey("drinks.drink_id"))

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    address_to = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    food_id = Column(Integer, ForeignKey("foods.food_id"))
    drink_id = Column(Integer, ForeignKey("drinks.drink_id"))


# class FavoriteFood(Base):
#     __tablename__ = "favorite_foods"
#
#     favorite_food_id = Column(Integer, nullable=False, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     food_id = Column(Integer, ForeignKey("foods.food_id"))

class FavoriteFood(Base):
    __tablename__ = "favorite_foods"

    favorite_food_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    food_id = Column(Integer, ForeignKey("foods.food_id"))


# class Food(Base):
#     __tablename__ = "foods"
#
#     food_id = Column(Integer, nullable=False, primary_key=True)
#     kind = Column(String(255), nullable=False)
#     price = Column(Integer, nullable=False)
#     cook_time = Column(Integer, nullable=False)
#     image = Column(String(255), nullable=False)
#     food_name = Column(String(255), nullable=False)
#     description = Column(String(255), nullable=False)
#     rating = Column(Float, nullable=False)
#     restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))


class Food(Base):
    __tablename__ = "foods"

    food_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    kind = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    cook_time = Column(Integer, nullable=False)
    image = Column(String(255), nullable=False)
    food_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))


# class WorkTime(Base):
#     __tablename__ = "work_time"
#
#     work_time_id = Column(Integer, nullable=False, primary_key=True)
#     day_of_week = Column(String(255), nullable=False)
#     opening_time = Column(String(255), nullable=False)
#     closing_time = Column(String(255), nullable=False)
#     restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))


class WorkTime(Base):
    __tablename__ = "work_time"

    work_time_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    day_of_week = Column(String(255), nullable=False)
    opening_time = Column(String(255), nullable=False)
    closing_time = Column(String(255), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    restaurant_name = Column(String(255), nullable=False)
    kind = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    restaurant_email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    logo = Column(String(255), nullable=False)
    background_image = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)

#
# class FavoriteRestaurant(Base):
#     __tablename__ = "favorite_restaurants"
#
#     favorite_restaurant_id = Column(Integer, nullable=False, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
#
#
# class RessetPassword(Base):
#     __tablename__ = "password_reset"
#
#     password_resset_id = Column(Integer, nullable=False, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     code = Column(Integer, nullable=False, unique=True)
#
#
# class Drinks(Base):
#     __tablename__ = "drinks"
#
#     drink_id = Column(Integer, nullable=False, primary_key=True)
#     kind = Column(String(255), nullable=False)
#     price = Column(Integer, nullable=False)
#     image = Column(String(255), nullable=False)
#     drink_name = Column(String(255), nullable=False)
#     description = Column(String(255), nullable=False)
#     rating = Column(Float, nullable=False)
#     restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
#



class FavoriteRestaurant(Base):
    __tablename__ = "favorite_restaurants"

    favorite_restaurant_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))

class ResetPassword(Base):
    __tablename__ = "password_reset"

    password_reset_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    code = Column(Integer, nullable=False, unique=True)

class Drinks(Base):
    __tablename__ = "drinks"

    drink_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    kind = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(255), nullable=False)
    drink_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))