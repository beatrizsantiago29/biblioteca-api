# 📚 Sistema de Gerenciamento de Biblioteca

API REST desenvolvida para gerenciamento de biblioteca, incluindo controle de acervos, empréstimos e usuários. O projeto foca em boas práticas de desenvolvimento, utilizando **FastAPI** para alta performance e **SQLAlchemy** como ORM para persistência e manipulação de dados.


## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/)
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Banco de Dados:** SQLite
* **Migrações:** [Alembic](https://alembic.sqlalchemy.org/)
* **Validação de Dados:** Pydantic

## 🛠️ Funcionalidades

O sistema permite o gerenciamento completo do ciclo de vida de uma biblioteca:

- **Gerenciamento de Usuários:** Cadastro de leitores e administradores.
- **Gestão de Livros:** Cadastro (Título, Autor, ISBN), edição, listagem e exclusão (CRUD).
- **Sistema de Empréstimos:** Registro de saída e devolução de obras com verificação automática de disponibilidade.

## ⚙️ Como Executar o Projeto

### Pré-requisitos
* Python 3.10 ou superior.
* Ambiente virtual (venv) recomendado.

### Passo a Passo

1. **Clone o repositório:**
   ```
   git clone [https://github.com/seu-usuario/nome-do-repo.git](https://github.com/seu-usuario/nome-do-repo.git)
   cd nome-do-repositorio
   ```

2. **Crie e ative o ambiente virtual:**
    ```
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No Linux/Mac:
    source venv/bin/activate
    ```

3. **Instale as dependências:**
    ```
    pip install -r requirements.txt
    ```

4. **Migrações do Banco de Dados:** 
    Certifique-se de que a sqlalchemy.url no arquivo alembic.ini (ou sua configuração de ambiente) aponta para o seu banco. Então, execute:
    ```
    alembic upgrade head
    ```

5. **Inicie o servidor:**
    ```
    uvicorn main:app --reload
    ```

    Acesse a documentação interativa (Swagger UI) em: `http://127.0.0.1:8000/docs`

## 🛠️ Endpoints Principais

A API segue o padrão REST e você pode testar todos os endpoints diretamente pela interface do Swagger em `/docs`.

### Cadastro e login
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **POST** | `/auth/cadastrar_usuario` | Rota padrão de cadastro de usuário |
| **POST** | `/auth/login` | Rota padrão de login de usuários |
| **POST** | `/auth/login-form` | Login através da documentação (Botão "Authorize") |

### Livros
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **GET** | `/book` | Lista todos os livros cadastrados |
| **POST** | `/book/cadastrar_livro` | Cadastra um novo livro no acervo |
| **DELETE** | `/book/excluir/{id}` | Remove um livro do sistema |


### Empréstimos
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **GET** | `/emprestimo` | Lista todos os empréstimos realizados |
| **POST** | `/emprestimo/alugar/{id_livro}` | Registra um novo empréstimo (vínculo Usuário-Livro) |
| **PATCH** | `/emprestimo/devolucao/{id_emprestimo}` | Registra a devolução de um exemplar |

---
