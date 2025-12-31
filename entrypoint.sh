#!/bin/sh

# Se der qualquer erro, para tudo imediatamente (Segurança)
set -e

echo "🛠️  Verificando migrações do Banco de Dados..."
python manage.py migrate --noinput

echo "🎨  Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🚀  Iniciando o Servidor (Gunicorn)..."
# Executa o comando que está no docker-compose (o gunicorn)
exec "$@"
