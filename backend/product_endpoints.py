from pydantic import BaseModel, HttpUrl
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException,APIRouter
from typing import List, Optional
from backend.database import get_db  ,Session
from urllib.parse import quote


app = FastAPI()
product_balance_router = APIRouter()



#----------------------Список товара через фильтр-------------------------------------------------------
class ProductInfo(BaseModel):
    магазин: str
    провайдер: str
    остаток_колво: int
    товар: str
    vendor_code: str
    barcode: Optional[str]
    картинка: Optional[HttpUrl] = None

    class Config:
        from_attributes = True



@product_balance_router.post("/products/", response_model=List[ProductInfo])
def read_products(store: Optional[List[str]] = None, provider: Optional[List[str]] = None, include_image: bool = False, db: Session = Depends(get_db)):
    query = """
    SELECT 
        s."name" AS магазин,
        p2."name" AS провайдер,
        SUM(ps.count) AS остаток_колво,
        p."name" AS товар,
        p.vendor_code,
        MAX(pb.barcode) AS barcode,
        'https://zerdetoys.assistant.org.kz:9008/images/' || fi.stored_path AS картинка
    FROM 
        product_supply ps 
    JOIN product p ON p.id = ps.product_id 
    JOIN product_barcode pb ON pb.product_id = p.id 
    JOIN provider p2 ON p2.id = ps.provider_id
    JOIN store s ON s.id = ps.store_id 
    LEFT JOIN product_image pi2 ON pi2.product_id = p.id AND pi2.is_main IS TRUE
    LEFT JOIN file_info fi ON fi.id = pi2.file_info_id 
    WHERE 1=1
    """.format("'https://zerdetoys.assistant.org.kz:9008/images/' || fi.stored_path" if include_image else "NULL")

    if store:
        query += " AND s.\"name\" IN :store"
    if provider:
        query += " AND p2.\"name\" IN :provider"
    
    query += " GROUP BY s.\"name\", p2.\"name\", p.\"name\", p.vendor_code, fi.stored_path"

    try:
        result = db.execute(query, {'store': tuple(store), 'provider': tuple(provider)}).fetchall()
        # Преобразуем данные в список словарей для кодирования URL картинок
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

#----------------------Провайдер-------------------------------------------------------
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