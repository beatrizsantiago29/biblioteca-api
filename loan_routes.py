from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Livro, Emprestimo, Usuario
from datetime import timedelta, timezone, datetime

loan_router = APIRouter(prefix="/emprestimo", tags=["emprestimo"], dependencies=[Depends(verificar_token)])

# Rota principal: lista os emprestimo do usuario
@loan_router.get("/")
async def listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    dados = session.query(Emprestimo.id_livro, Emprestimo.data_emprestimo, Emprestimo.data_devolucao).filter(Emprestimo.id_usuario == usuario.id, Emprestimo.status == "ativo")
    emprestimos = {t[0] : (t[1], t[2]) for t in dados}
    if not emprestimos:
        return {"mensagem": "Nenhum empréstimo registrado."}
    else:
        return emprestimos

# Rota de alugar livro:
# verifica se o livro é válido, se o usuário já possui empréstimo do livro e se há cópias disponíveis
# para empréstimo.
@loan_router.post("/alugar/{id_livro}")
async def alugar(id_livro: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    # verificar se existe o usuario ja alugou o livro
    emprestimo = session.query(Emprestimo).filter(Emprestimo.id_livro == id_livro, Emprestimo.id_usuario == usuario.id, Emprestimo.status == "ativo").first()
    if emprestimo:
        return {
            "mensagem": f"Já existe um empréstimo ativo do livro {id_livro} na sua conta."
        }
    
    # verificar se o livro é valido e caso seja, verificar se há cópias disponíveis para empréstimo
    livro = session.query(Livro).filter(Livro.id == id_livro).first()
    if not livro:
        raise HTTPException(status_code=400, detail="Livro não encontrado.")
    elif livro.qtd_disponivel <= 0:
        return {"mensagem": "Não há cópias disponíveis para empréstimo."}
    else:
        data_dev = datetime.now(timezone.utc) + timedelta(days=30)
        novo_emprestimo = Emprestimo(id_livro = livro.id, id_usuario=usuario.id, data_devolucao=data_dev)
        livro.qtd_disponivel -= 1
        session.add(novo_emprestimo)
        session.commit()
        return {"mensagem": f"Emprestimo criado com sucesso.",
                "livro": livro
                }