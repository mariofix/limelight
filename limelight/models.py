from cthulhu.database import db
from sqlalchemy.dialects import mysql
from cthulhu.models import TimestampMixin


class Product(db.Model, TimestampMixin):
    __tablename__ = "limelight_product"
    __allow_unmapped__ = True

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    allergen = db.Column(db.String(64), nullable=True, default=None)
    organic = db.Column(db.Boolean(), default=False)
    vegan = db.Column(db.Boolean(), default=False)
    type = db.Column(db.String(64), nullable=True, default=None)  # Cambiar a Enum
    brand = db.Column(db.String(64), nullable=True, default=None)
    weight = db.Column(db.Integer(), nullable=True, default=None)  # gramos
    volume = db.Column(db.Float(), nullable=True, default=None)  # litros
    nutritional_facts: db.Column(mysql.JSON, nullable=True, default=None)

    ingredients = db.relationship("Ingredient")

    def __str__(self):
        return self.name


class Recipe(db.Model, TimestampMixin):
    __tablename__ = "limelight_recipe"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    time = db.Column(db.Integer())  # minutos
    # picture: Path
    # instructions: Text | markdown | stepbystep
    # vegetarian: Bool
    # high_protein: Bool

    ingredients = db.relationship("Ingredient")


class Ingredient(db.Model, TimestampMixin):
    __tablename__ = "limelight_ingredient"

    id = db.Column(db.Integer(), primary_key=True)

    product_id = db.Column(db.Integer(), db.ForeignKey("limelight_product.id"))
    products = db.relationship("Product", back_populates="ingredients")

    recipe_id = db.Column(db.Integer(), db.ForeignKey("limelight_recipe.id"))
    recipes = db.relationship("Recipe", back_populates="ingredients")

    quantity = db.Column(db.String(64), nullable=True, default=None)  # Cambiar a Enum
