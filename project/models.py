from flask_login import UserMixin
from sqlalchemy import create_engine, Text, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship

from config import db


DATABASE_URL = 'sqlite:///blog.db'
engine = create_engine(DATABASE_URL, echo=True)
session = Session(engine, expire_on_commit=True, autoflush=False)


class Base(DeclarativeBase, UserMixin):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    posts: Mapped[list["Post"]] = relationship(back_populates="user", uselist=False, cascade="all, delete")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=False)
    user: Mapped["Author"] = relationship(back_populates="posts", uselist=True)
