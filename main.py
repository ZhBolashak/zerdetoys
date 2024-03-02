from fastapi import FastAPI
from product_balance import product_balance_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.include_router(product_balance_router, prefix="/api/v1")


# Позволить запросы со всех доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает все домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы
    allow_headers=["*"],  # Разрешает все заголовки
)