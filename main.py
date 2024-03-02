from fastapi import FastAPI
from product_balance import product_balance_router
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi import Request
from fastapi.logger import logger as fastapi_logger

# Настройте логгер
gunicorn_logger = logging.getLogger('gunicorn.error')
fastapi_logger.handlers = gunicorn_logger.handlers
if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    logging.basicConfig(level=logging.DEBUG)

# Теперь вы можете использовать fastapi_logger для логирования
fastapi_logger.debug("Debug message")
fastapi_logger.info("Info message")




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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    fastapi_logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    fastapi_logger.debug(f"Response status: {response.status_code}")
    return response
