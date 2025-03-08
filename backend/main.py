# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routes import home, piezas, pedidos  # Importar los routers
from backend.database import engine
from backend.models import Base  # Asegúrate de importar los modelos

app = FastAPI()

# Montar los archivos estáticos
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Incluir los routers
app.include_router(home.router)
app.include_router(piezas.router)
app.include_router(pedidos.router)

# Crear las tablas de la base de datos (asegúrate de que las tablas se creen al arrancar el servidor)
Base.metadata.create_all(bind=engine)
