from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurar la base de datos SQLite
DATABASE_URI = 'sqlite:///app.db'
engine = create_engine(DATABASE_URI, echo=True)

Base = declarative_base()

# Modelo de la tabla Book
class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    series = Column(String(100), nullable=True)
    published_date = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(300), nullable=True)

# Crear todas las tablas
Base.metadata.create_all(engine)

print("La base de datos y la tabla 'book' han sido inicializadas.")
