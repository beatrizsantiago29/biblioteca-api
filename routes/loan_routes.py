from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Livro, Emprestimo, Usuario
from datetime import timedelta, timezone, datetime

# Precisa de usuario logado
loan_router = APIRouter(prefix="/emprestimo", tags=["emprestimo"], dependencies=[Depends(verificar_token)])

# Rota principal: lista os emprestimos do usuario
@loan_router.get("/")
async def listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    dados = session.query(Emprestimo).filter(Emprestimo.id_usuario == usuario.id).all()
    if not dados:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Nenhum emprestimo registrado")
    else:
        return {"emprestimos" : dados}

# Lista emprestimos ativos do usuario
@loan_router.get("/listar_emprestimos_ativos")
async def listar_ativos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    dados = session.query(Emprestimo).filter(Emprestimo.id_usuario == usuario.id, Emprestimo.status == "ativo").all()
    if not dados:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Nenhum emprestimo ativo")
    else:
        return {"emprestimos" : dados}


# Rota de alugar livro:
# verifica se o livro é válido, se o usuário já possui empréstimo do livro e se há cópias disponíveis
# para empréstimo.
@loan_router.post("/alugar/{id_livro}", status_code=status.HTTP_201_CREATED)
async def alugar(id_livro: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    # verificar se o usuario ja alugou o livro
    emprestimo = session.query(Emprestimo).filter(Emprestimo.id_livro == id_livro, Emprestimo.id_usuario == usuario.id, Emprestimo.status == "ativo").first()
    if emprestimo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Já existe um empréstimo ativo para o livro {id_livro}")
    
    # verificar se o livro é valido e caso seja, verificar se há cópias disponíveis para empréstimo
    livro = session.query(Livro).filter(Livro.id == id_livro).first()
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    elif livro.qtd_disponivel <= 0:
        return {"mensagem": "Não há cópias disponíveis para empréstimo."}
    else:
        data_dev = datetime.now(timezone.utc) + timedelta(days=30)
        novo_emprestimo = Emprestimo(id_livro = livro.id, id_usuario=usuario.id, data_devolucao=data_dev)
        livro.qtd_disponivel -= 1
        session.add(novo_emprestimo)
        session.commit()
        return {"mensagem": f"Empréstimo do livro {livro.titulo} criado com sucesso.",
                "livro": livro
                }
    
# rota de devolução de livro
@loan_router.patch("/devolucao/{id_livro}")
async def devolver(id_livro: int, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    emprestimo = session.query(Emprestimo).filter(Emprestimo.id_usuario == usuario.id, Emprestimo.id_livro == id_livro, Emprestimo.status == "ativo").first()
    if not emprestimo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não existe um empréstimo ativo registrado para o livro {id_livro}")
    else:
        livro = session.query(Livro).filter(Livro.id == id_livro).first()
        livro.qtd_disponivel += 1
        emprestimo.status = "concluido"
        session.commit()
        return {"mensagem": f"Devolução do livro {id_livro} concluída com sucesso."}