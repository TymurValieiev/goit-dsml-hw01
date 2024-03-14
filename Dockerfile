# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.12.1-slim

# Встановимо змінну середовища
ENV MAIN_HOME /main

# Встановимо робочу директорію всередині контейнера
WORKDIR $MAIN_HOME

# Встановимо залежності всередині контейнера
COPY pyproject.toml $MAIN_HOME/pyproject.toml
COPY poetry.lock $MAIN_HOME/poetry.lock

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main


# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 5000

# Запустимо наш застосунок всередині контейнера
ENTRYPOINT ["python", "main.py"]
