from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, registry

# Создаем объект registry, который будет использоваться для конфигурации моделей
mapper_registry = registry()

# Создаем базовый класс для моделей
Base = mapper_registry.generate_base()

# Настраиваем подключение к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/document_management_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Настройка всех мапперов после объявления моделей
mapper_registry.configure()
