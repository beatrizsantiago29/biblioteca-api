from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv() # carregar variaveis de ambiente

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI() # criação do APP, instância de FastAPI

# schemes: modelos de criptografia
# deprecated: caso um schema de criptografia se torne obsoleto,
# ele será automaticamente descartado 
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from book_routes import book_router
from loan_routes import loan_router
from author_routes import author_router

# incluindo rotas
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(loan_router)
app.include_router(author_router)
# para rodar o código, executar no terminal: uvicorn main:app --reload