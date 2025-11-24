# Etapa 1: Construcción
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar Node.js (Necesario para compilar el frontend de Reflex)
RUN apt-get update && apt-get install -y nodejs npm curl unzip

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Configurar URL para la compilación (Esto es clave)
ARG API_URL="http://localhost:8000"
ENV API_URL=${API_URL}
ENV BUN_INSTALL="/root/.bun"

# Instalar Reflex y exportar el Frontend
# Esto genera la carpeta .web/_static con el HTML/JS final
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Etapa 2: Ejecución (Imagen final ligera)
FROM python:3.11-slim

WORKDIR /app

# Instalar Nginx y dependencias básicas
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copiar dependencias de Python de la etapa anterior
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/reflex /usr/local/bin/reflex

# Copiar el código del backend y el frontend compilado
COPY . .
COPY --from=builder /app/.web/_static /app/public

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Comando de arranque: Inicia Nginx (Frontend) y Reflex (Backend) juntos
CMD service nginx start && reflex run --env prod --backend-only
