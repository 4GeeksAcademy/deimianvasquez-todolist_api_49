from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


# En la base de datos no se guarda las imagenes, se guarda la url que referencia a esa imagen
class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    avatar: Mapped[str] = mapped_column(String(
        180), nullable=False, default="https://randomuser.me/api/portraits/women/41.jpg")
    create_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    todos: Mapped[list["Todos"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

    # Método de serializado --> Pasa la clase de su tipo a un diccionario
    # podemos tener cuantos serializados necesitemos
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "avatar": self.avatar,
            # "todos": [item.serialize() for item in self.todos] --> list complehensions
            "todos": list(map(lambda item: item.serialize(), self.todos))
            # OJO, LA PASSWORD NO SE SERIALIZA
        }


class Todos(db.Model):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_done: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    create_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"))  # llave foranea

    user: Mapped["User"] = relationship(
        back_populates="todos")

    def serialize(self):
        return {
            "id": self.id,
            "label": self.label,
            "is_done": self.is_done,
            "user_id": self.user_id
        }
