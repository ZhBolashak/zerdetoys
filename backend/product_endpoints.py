from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from backend.database import get_db, Session
from urllib.parse import quote

app = FastAPI()
product_balance_router = APIRouter()

class ProductInfo(BaseModel):
    магазин: str
    провайдер: Optional[str]
    остаток_колво: int
    оптовая_цена: int
    розничная_цена: int
    товар: str
    vendor_code: str
    barcode: Optional[str]
    картинка: Optional[HttpUrl] = None

    class Config:
        orm_mode = True  # Если вы используете ORM

@product_balance_router.post("/products/", response_model=List[ProductInfo])
def read_products(store: Optional[List[str]] = None, provider: Optional[List[str]] = None, include_image: bool = False, db: Session = Depends(get_db)):
    # Использование обновлённого запроса с CTE
    query = """
    WITH RankedSupplies AS (
        SELECT 
            s."name" AS "магазин",
            p2."name" AS "провайдер",
            p."name" AS "товар",
            p.vendor_code,
            ps.count AS "остаток_колво",
            ps.trade_price AS "оптовая_цена",
            ps.retail_price AS "розничная_цена",
            MAX(pb.barcode) OVER (PARTITION BY p.id) AS barcode,
            'https://zerdetoys.assistant.org.kz:9008/images/' || fi.stored_path AS "картинка",
            ROW_NUMBER() OVER (PARTITION BY s.id, p2.id, p.id ORDER BY ps.created_on DESC) AS rn
        FROM 
            product_supply ps 
        JOIN product p ON p.id = ps.product_id 
        JOIN product_barcode pb ON pb.product_id = p.id 
        JOIN provider p2 ON p2.id = ps.provider_id
        JOIN store s ON s.id = ps.store_id 
        LEFT JOIN product_image pi2 ON pi2.product_id = p.id AND pi2.is_main IS TRUE
        LEFT JOIN file_info fi ON fi.id = pi2.file_info_id 
    )
    SELECT 
        магазин,
        провайдер,
        товар,
        vendor_code,
        остаток_колво,
        оптовая_цена,
        розничная_цена,
        barcode,
        картинка
    FROM RankedSupplies
    WHERE rn = 1
    """

    params = {}
    if store:
        query += " AND магазин IN :store"
        params['store'] = tuple(store)
    if provider:
        query += " AND провайдер IN :provider"
        params['provider'] = tuple(provider)
    
    try:
        result = db.execute(query, params).fetchall()
        products_info = []
        for row in result:
            product = dict(row)
            if product['картинка']:
                product['картинка'] = quote(product['картинка'], safe=':/')
            products_info.append(product)
        return products_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#----------------------Провайдер-------------------------------------------------------
class Provider(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@product_balance_router.get("/providers", response_model=List[Provider])
def get_providers(db: Session = Depends(get_db)):
    try:
        # Выполнение запроса к базе данных
        providers = db.execute("SELECT id, name FROM provider").fetchall()
        # Преобразование результатов в список словарей
        return [{"id": id, "name": name} for id, name in providers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------Магазин-------------------------------------------------------
class Stores(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@product_balance_router.get("/stores", response_model=List[Stores])
def get_stores(db: Session = Depends(get_db)):
    try:
        # Выполнение запроса к базе данных
        store = db.execute("SELECT id, name FROM store").fetchall()
        # Преобразование результатов в список словарей
        return [{"id": id, "name": name} for id, name in store]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
