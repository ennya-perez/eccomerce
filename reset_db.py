# reset_db.py
from sqlmodel import SQLModel
from app.core.db import engine

# ¡Ojenés que importar todos los modelos para que SQLModel arme el mapa de relaciones
from app.models.user import AppUser
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import Order
# Si reaste order.py, impórtalo también acá

def resetear_postgres():
    print("Conectando a Postgres y borrando tablas viejas...")
    # SQLModel es inteligente: gracias a Postgres, borra todo en cascada respetando las relaciones
    SQLModel.metadata.drop_all(engine)

if __name__ == "__main__":
    resetear_postgres()