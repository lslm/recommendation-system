from src.api.routes import router as api_router
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Registrar as rotas da API
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
