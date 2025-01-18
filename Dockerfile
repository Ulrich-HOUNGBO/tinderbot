# syntax=docker/dockerfile:1
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définissez /app comme répertoire de travail
WORKDIR /app

# Copiez les fichiers de l'application dans le conteneur
COPY . .

RUN pip install -r requirements.txt

# RUN python manage.py makemigrations
# RUN python manage.py migrate

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
