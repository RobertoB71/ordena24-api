from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.categorias import router as categorias_router

app = FastAPI(
    title="Ordena24 API",
    description="API REST para la gestión de productos y pedidos del restaurante Ordena24.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categorias_router)


@app.get("/")
def home():
    return {
        "message": "API de Ordena24 funcionando correctamente"
    }