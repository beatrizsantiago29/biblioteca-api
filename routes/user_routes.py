from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Usuario, Emprestimo
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema

user_router = APIRouter(prefix="/user", tags=["user"])

# Rota de editar usuário para usuários comuns
@user_router.put("/editar")
async def editar(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    usuario.email = usuario_schema.email
    usuario.nome = usuario_schema.nome
    usuario.admin = usuario_schema.admin
    # criptografar senha antes de salvar no banco
    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    usuario.senha = senha_criptografada
    session.commit()
    session.refresh(usuario)
    return {"mensagem" : f"Usuário {usuario.email} atualizado com sucesso!"}

# Rota de excluir/desativar usuário para usuários comuns
@user_router.delete("/excluir")
async def excluir(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    emprestimos = session.query(Emprestimo).filter(Emprestimo.id_usuario == usuario.id).all()
    if not emprestimos:
        session.delete(usuario)
        session.commit()
        return {
            "mensagem" : f"Usuário {usuario.id} excluído com sucesso."
        }
    else:
        for e in emprestimos:
            if e.status == "ativo":
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário possui empréstimos ATIVOS. Por favor, devolver livros antes de desativar conta.")
        usuario.ativo = False
        session.commit()
        session.refresh(usuario)
        return {
            "mensagem" : f"Usuário {usuario.id} possui empréstimos registrados, usuário desativado com sucesso."
        }

# Rota de listar todos os usuários para admin
@user_router.get("/")
async def listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para fazer essa ação.")
    usuarios = session.query(Usuario).all()
    return {
        "usuarios" : usuarios
    }

# Rota de editar usuário para admin
@user_router.put("/{id_usuario}")
async def editar(id_usuario: int, usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para fazer essa ação.")
    usuario_ = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuário {id_usuario} não encontrado.")
    usuario_.email = usuario_schema.email
    usuario_.nome = usuario_schema.nome
    usuario_.admin = usuario_schema.admin
    # criptografar senha antes de salvar no banco
    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    usuario_.senha = senha_criptografada
    session.commit()
    session.refresh(usuario_)
    return {"mensagem" : f"Usuário {usuario_.email} atualizado com sucesso!"}

# Rota para excluir usuário para admin
@user_router.delete("/{id_usuario}")
async def excluir(id_usuario: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para fazer essa ação.")
    usuario_ = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    else:
        # Verificar se o usuário está associado a algum empréstimo
        emprestimos = session.query(Emprestimo).filter(Emprestimo.id_usuario == usuario_.id).all()
        if not emprestimos:
            session.delete(usuario_)
            session.commit()
            return {
                "mensagem" : f"Usuário {usuario_.id} excluído com sucesso."
            }
        else:
            for e in emprestimos:
                if e.status == "ativo":
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário possui empréstimos ATIVOS. Por favor, devolver livros antes de desativar conta.")
            usuario_.ativo = False
            session.commit()
            session.refresh(usuario_)
            return {
                "mensagem" : f"Usuário {usuario_.id} possui empréstimos registrados, usuário desativado com sucesso."
            }