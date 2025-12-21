from server import app as vercel_app

# Vercel використовує цей файл як entrypoint для serverless-функції.
# FastAPI-додаток має бути доступний через змінну з назвою vercel_app.