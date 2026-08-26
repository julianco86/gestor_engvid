FROM python:3.10-slim

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY . .

RUN python src/crearBD.py

EXPOSE 8000

CMD ["python", "src/iniciar.py"]
