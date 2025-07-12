# Используем официальный Python-образ
FROM python:3.13

# Устанавливаем LibreOffice
RUN apt-get update && apt-get install -y \
    gnupg \
    apt-utils \
    apt-transport-https \
    software-properties-common \
    wget \
    curl \
    ca-certificates \
    libreoffice \
    libreoffice-writer \
    libreoffice-core \
    libreoffice-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

# Копируем проект
COPY . .

# Запускаем FastAPI-приложение через uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]