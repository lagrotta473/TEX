## Projeto Django no Docker

Para acessar o projeto Django, siga os passos abaixo:

1. **Iniciar os serviços Docker:**
   ```bash
   docker-compose up
   ```

2. **Acessar o Django Admin:**
   Abra seu navegador e vá para `http://localhost:8000/admin/`

3. **Comandos úteis:**
   - Criar superusuário: `docker-compose run web python manage.py createsuperuser`
   - Rodar migrações: `docker-compose run web python manage.py migrate`
   - Criar um novo app: `docker-compose run --rm web python manage.py startapp <app_name>`
