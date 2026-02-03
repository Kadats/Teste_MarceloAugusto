from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configurações (Mesmas do importer.py)
# Em produção, usaríamos variáveis de ambiente (.env), mas vamos manter hardcoded pro teste (KISS)
DB_USER = "user_ans"
DB_PASS = "password_ans"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ans_database"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria o motor de conexão
engine = create_engine(DATABASE_URL)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos (se fossemos usar ORM completo, mas usaremos SQL direto para performance)
Base = declarative_base()

# Dependência (Função que o FastAPI chama para pegar o banco)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

