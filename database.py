from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL подключения к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/document_management_db"

# Создание движка базы данных для выполнения операций с PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Размер пула соединений
    max_overflow=0  # Ожидание вместо переполнения пула соединений
)

# Фабрика сессий для работы с базой данных (автофиксация и автоочистка отключены)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей данных
Base = declarative_base()
Base.metadata.create_all(bind=engine)

# Функция для получения сессии базы данных
# Используется как зависимость FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db  # Передача сессии в маршруты FastAPI
    finally:
        db.close()  # Закрытие сессии после завершения работы
