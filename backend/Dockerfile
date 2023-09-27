FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
# COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
COPY . /code/
RUN pip install -r ./requirements.txt
RUN pip install .
WORKDIR /code/web
EXPOSE 8001
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]