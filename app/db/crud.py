from sqlalchemy.orm import Session
from app.models.film import Film
from app.models.genre import Genre
from app.models.actor import Actor
from app.models.director import Director
from app.models.keyword import Keyword

def get_film_by_title(db: Session, title: str):
    return db.query(Film).filter(Film.title == title).first()

def add_film(db: Session, title: str, year: int, description: str, rating: float, poster: str):
    film = Film(title=title, year=year, description=description, rating=rating, poster=poster)
    db.add(film)
    db.commit()
    db.refresh(film)
    return film

def get_or_create_genre(db: Session, name: str):
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.commit()
        db.refresh(genre)
    return genre

def get_or_create_actor(db: Session, name: str):
    actor = db.query(Actor).filter(Actor.name == name).first()
    if not actor:
        actor = Actor(name=name)
        db.add(actor)
        db.commit()
        db.refresh(actor)
    return actor

def get_or_create_director(db: Session, name: str):
    director = db.query(Director).filter(Director.name == name).first()
    if not director:
        director = Director(name=name)
        db.add(director)
        db.commit()
        db.refresh(director)
    return director

def get_or_create_keyword(db: Session, name: str):
    keyword = db.query(Keyword).filter(Keyword.name == name).first()
    if not keyword:
        keyword = Keyword(name=name)
        db.add(keyword)
        db.commit()
        db.refresh(keyword)
    return keyword
