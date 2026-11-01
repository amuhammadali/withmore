FROM node:22-alpine AS web-build
WORKDIR /web
COPY frontend/package.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv/backend \
    FRONTEND_DIST=/srv/frontend/dist
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt psycopg[binary]>=3.2
COPY backend/ ./backend/
COPY --from=web-build /web/dist ./frontend/dist
EXPOSE 8000
CMD ["sh", "-c", "python -m app.manage init && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

