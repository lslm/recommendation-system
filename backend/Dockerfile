# Escolher a imagem base com Python 3.10.16
FROM python:3.10.16-slim

# Instalar dependências do sistema para rodar a aplicação e o Poetry
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Adicionar o Poetry ao PATH
ENV PATH="/root/.local/bin:$PATH"

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de dependências (como pyproject.toml) para o contêiner
COPY pyproject.toml poetry.lock /app/

# Instalar as dependências do projeto com Poetry
RUN poetry install --no-root

# Copiar o código-fonte da aplicação para dentro do contêiner
COPY src /app/src

# Expor a porta que o servidor vai rodar
EXPOSE 8000

# Comando para rodar a aplicação FastAPI
CMD ["poetry", "run", "python", "-m", "src.api.server"]

