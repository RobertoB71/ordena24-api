from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.categorias import router as categorias_router
from routes.productos import router as productos_router
from routes.pedidos import router as pedidos_router
from routes.auth import router as auth_router
from routes.usuarios import router as usuarios_router


app = FastAPI(
    title="Ordena24 API",
    description="API REST para la gestión de usuarios, productos y pedidos del restaurante Ordena24.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(pedidos_router)


@app.get("/")
def home():
    return {"message": "API de Ordena24 funcionando correctamente"}