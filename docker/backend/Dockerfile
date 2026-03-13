FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/link_forge ./link_forge

CMD ["sh", "-c", "python -m link_forge"]
