from fastapi import Depends, HTTPException
from models import db, Usuario
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_schema

# Funcao que cria uma sessao (instancia) de conexao com o banco
def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

# Funcao que verifica se um token eh valido e retorna o usuario do token
def verificar_token(token:str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    # verificar token
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token")
    # achar usuario
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso inválido")
    return usuario

def verificar_admin(usuario: Usuario = Depends(verificar_token)):
    if usuario.admin: return True
    raise HTTPException(status_code=401, detail="Acesso negado.")