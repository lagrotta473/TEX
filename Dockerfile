# ==========================================
# ESTÁGIO 1: A FÁBRICA (Builder)
# ==========================================
# Usamos Python 3.11 para suportar Django 5.0
FROM python:3.11-slim as builder

# Evita arquivos temporários de pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalação de ferramentas de "chão de fábrica" (Compiladores)
# Necessário para compilar bibliotecas que mexem com C (como o driver do Postgres)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev

# Criação de um ambiente virtual (Isolamento da peça)
RUN python -m venv /opt/venv
# Habilita o ambiente virtual no PATH
ENV PATH="/opt/venv/bin:$PATH"

# Instalação das dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# ESTÁGIO 2: O PRODUTO FINAL (Runner)
# ==========================================
# Começamos de uma imagem limpa (Alpine ou Slim). Jogamos o "builder" fora.
FROM python:3.11-slim

WORKDIR /app

# Instala apenas as bibliotecas de sistema necessárias para RODAR (não compilar)
# libpq5 é necessário para o Postgres funcionar
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copia o ambiente virtual PRONTO do estágio anterior (Builder)
COPY --from=builder /opt/venv /opt/venv

# Define que vamos usar o ambiente virtual por padrão
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código fonte do projeto
COPY . .

# Segurança (HSE): Não rodar como root. Criamos um usuário comum.
RUN useradd -m appuser
USER appuser

# Comando de start
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]