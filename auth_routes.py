from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import Usuario
from schemas import UsuarioSchema, LoginSchema
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime

# criando roteador de autenticação
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Funcao para criar tokens (access e refresh)
def criar_token(id_usuario:int, duracao=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao
    # sub: padrao para "id de usuario" como str
    dic_info = {"sub" : str(id_usuario), "exp" : data_expiracao}
    jwt_criptografado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)

    return jwt_criptografado

# Funcao de autenticacao do usuario (email e senha)
def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario


@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}


# rota de cadastro de usuario
@auth_router.post("/cadastrar_usuario")
async def cadastrar(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        # usuario ja existe
        raise HTTPException(status_code=400, detail="Credenciais ja cadastradas.")
    else:
        # criptografar senha antes de salvar no banco
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(nome=usuario_schema.nome, email=usuario_schema.email, senha=senha_criptografada, admin=usuario_schema.admin)

        # adicionar usuario
        session.add(novo_usuario)

        # realizar o commit no banco
        session.commit()

        return {"mensagem":f"usuario {usuario_schema.email} cadastrado com sucesso"}
    

# rota de login
# login -> email e senha -> token JWT
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    else:
        # JWT Bearer
        # headers = {"Access-Token":"Bearer token"}
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao=timedelta(days=7))
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"Bearer"
        }


# rota de login da documentacao (Bearer)
@auth_router.post("/login-form")
async def login_form(dados_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_form.username, dados_form.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token":access_token,
            "token_type":"Bearer"
        }


# rota de refresh token
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token":access_token,
        "token_type":"Bearer"
    }