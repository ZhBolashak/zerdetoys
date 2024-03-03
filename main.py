from fastapi import FastAPI
from product_balance import product_balance_router

app = FastAPI()


app.include_router(product_balance_router, prefix="/api/v1")
