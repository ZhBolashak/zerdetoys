#main.py
from fastapi import FastAPI
from backend.product_endpoints import product_balance_router
from backend.sale_endpoints import sales_router
from backend.debt_endpoints import debt_router
from backend.cash_flow_costs import costs_router
from backend.credit_endpoints import credit_router

from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(product_balance_router, prefix="/api/v1", tags=["Остаток товара"])
app.include_router(sales_router, prefix="/api/dds", tags=["ДДС"])
app.include_router(debt_router, prefix="/api/debt", tags=["Дебиторка"])
app.include_router(credit_router, prefix="/api/credits", tags=["Кредиторка"])
app.include_router(costs_router, prefix="/api/costs", tags=["Расходы"])



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"General exception: {exc}", exc_info=True)
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)