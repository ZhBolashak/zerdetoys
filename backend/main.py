#main.py
from fastapi import FastAPI
from backend.product_endpoints import product_balance_router
from backend.sale_endpoints import sales_router

app = FastAPI()

app.include_router(product_balance_router, prefix="/api/v1", tags=["Остаток товара"])
app.include_router(sales_router, prefix="/api/dds", tags=["ДДС"])
