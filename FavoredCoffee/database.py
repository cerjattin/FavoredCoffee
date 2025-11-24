import os
from sqlmodel import SQLModel, create_engine, Session

# Leemos la URL de la base de datos de las variables de entorno
# Si no existe (local), usamos un sqlite temporal o falla
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback para local si no hay variable configurada
    sqlite_file_name = "database.db"
    DATABASE_URL = f"sqlite:///{sqlite_file_name}"

# Corrección necesaria para SQLAlchemy con URLs de Postgres en Render
# Render devuelve "postgres://", pero SQLAlchemy necesita "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session