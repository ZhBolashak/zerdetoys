from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text, Column, inspect, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

# Обновленные параметры подключения к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:aOwmK6%21h%5e15%40@87.255.194.116:5432/assistant_db"

# Создаем движок для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий, связанную с нашим движком
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Используем declarative_base для создания базового класса наших моделей
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Здесь вы можете добавить другие функции, связанные с базой данных,
# например, функции для выполнения определенных запросов к базе данных.
