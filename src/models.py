from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, String, Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

user_planet = Table(
    'user_planet',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('planet_id', Integer, ForeignKey('planet.id'), primary_key=True)
)

user_people = Table(
    'user_people',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('people_id', Integer, ForeignKey('people.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    planets = relationship('Planet', secondary=user_planet, back_populates='users')
    people = relationship('People', secondary=user_people, back_populates='users')

    def serialize(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "planets": [planet.id for planet in self.planets],
            "people": [person.id for person in self.people]
        }

class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    picture_url: Mapped[str] = mapped_column(String(255), nullable=True)

    users = relationship('User', secondary=user_planet, back_populates="planets")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "users": [user.id for user in self.users]
        }

class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    users = relationship('User', secondary=user_people, back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "users": [user.id for user in self.users]
        }
