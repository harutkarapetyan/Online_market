from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP

# revision identifiers, used by Alembic.
revision = 'f1bcb73c376d'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create `users` table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('phone_number', sa.String, nullable=False),
        sa.Column('address', sa.String, nullable=True),
        sa.Column('profile_image', sa.String, nullable=True),
        sa.Column('status', sa.Boolean, nullable=True, server_default="False"),
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text("now()")),
    )

    # Create `restaurants` table
    op.create_table(
        'restaurants',
        sa.Column('restaurant_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('restaurant_name', sa.String, nullable=False),
        sa.Column('kind', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('restaurant_email', sa.String, nullable=False, unique=True),
        sa.Column('phone_number', sa.String, nullable=False),
        sa.Column('address', sa.String, nullable=False),
        sa.Column('logo', sa.String, nullable=False),
        sa.Column('background_image', sa.String, nullable=False),
        sa.Column('rating', sa.Float, nullable=False)
    )

    # Create `cards` table
    op.create_table(
        'cards',
        sa.Column('card_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('card_number', sa.Integer, nullable=False),
        sa.Column('card_valid_thru', sa.String, nullable=False),
        sa.Column('card_name', sa.String, nullable=False),
        sa.Column('card_cvv', sa.Integer, nullable=False),
        sa.Column('status', sa.Boolean, nullable=False, server_default="False"),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id'))
    )

    # Create `foods` table
    op.create_table(
        'foods',
        sa.Column('food_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('kind', sa.String, nullable=False),
        sa.Column('price', sa.Integer, nullable=False),
        sa.Column('cook_time', sa.Integer, nullable=False),
        sa.Column('image', sa.String, nullable=False),
        sa.Column('food_name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('restaurant_id', sa.Integer, sa.ForeignKey('restaurants.restaurant_id'))
    )

    # Create `orders` table
    op.create_table(
        'orders',
        sa.Column('order_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('address_to', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id')),
        sa.Column('food_id', sa.Integer, sa.ForeignKey('foods.food_id'))
    )

    # Create `favorite_foods` table
    op.create_table(
        'favorite_foods',
        sa.Column('favorite_food_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id')),
        sa.Column('food_id', sa.Integer, sa.ForeignKey('foods.food_id'))
    )

    # Create `work_time` table
    op.create_table(
        'work_time',
        sa.Column('work_time_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('day_of_week', sa.String, nullable=False),
        sa.Column('opening_time', sa.String, nullable=False),
        sa.Column('closing_time', sa.String, nullable=False),
        sa.Column('restaurant_id', sa.Integer, sa.ForeignKey('restaurants.restaurant_id'))
    )

    # Create `favorite_restaurants` table
    op.create_table(
        'favorite_restaurants',
        sa.Column('favorite_restaurant_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id')),
        sa.Column('restaurant_id', sa.Integer, sa.ForeignKey('restaurants.restaurant_id'))
    )

    # Create `password_reset` table
    op.create_table(
        'password_reset',
        sa.Column('password_resset_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id')),
        sa.Column('code', sa.Integer, nullable=False, unique=True)
    )


def downgrade():
    # Drop all tables in reverse order of creation
    op.drop_table('password_reset')
    op.drop_table('favorite_restaurants')
    op.drop_table('work_time')
    op.drop_table('restaurants')
    op.drop_table('favorite_foods')
    op.drop_table('orders')
    op.drop_table('foods')
    op.drop_table('cards')
    op.drop_table('users')
