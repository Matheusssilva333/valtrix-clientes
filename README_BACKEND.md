# Valtrix Backend - Python Flask Edition 🚀

Este é o backend profissional, seguro e eficiente desenvolvido para a plataforma Valtrix. Migrado de Node.js para **Python Flask**, utilizando as melhores práticas de engenharia de software.

## 🌟 Principais Funcionalidades

- **Proxy Roblox Robusto**: Sistema de proxy inteligente que lida com redirecionamentos, headers de segurança e restrição de domínio (apenas `roblox.com`).
- **Banco de Dados Relacional**: Utiliza **SQLite** com **SQLAlchemy ORM** para armazenamento persistente e escalável (substituindo o antigo `db.json`).
- **Verificação de Inventário Real**: O endpoint de confirmação de compra agora verifica *realmente* se o usuário possui o item no inventário do Roblox antes de validar a comissão.
- **Sistema de Afiliados Automatizado**: Rastreamento de vendas e cálculo de comissões (10%) integrado ao banco de dados.
- **Segurança**: Proteção CORS, variáveis de ambiente (.env) e validação de input.

## 🛠️ Tecnologias Utilizadas

- **Framework**: Flask
- **ORM**: SQLAlchemy
- **Requisições**: Requests
- **Configuração**: Dotenv
- **Banco de Dados**: SQLite ( Valtrix.db )

## 🚀 Como Executar

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure o ambiente**:
   Renomeie ou edite o arquivo `.env` com suas chaves secretas.

3. **Inicie o servidor**:
   ```bash
   python app.py
   ```
   O servidor rodará em `http://localhost:5000`.

## 📂 Estrutura do Projeto

- `app.py`: Ponto de entrada com rotas e lógica principal.
- `models.py`: Definição dos esquemas do banco de dados.
- `requirements.txt`: Lista de dependências Python.
- `.env`: Configurações sensíveis.
- `valtrix.db`: Banco de dados gerado automaticamente.

---
Desenvolvido por **Antigravity** (Senior Fullstack Engineer)
