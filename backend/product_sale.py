#product_sale.py
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam

from backend.database import get_db

productorder_router = APIRouter()


# ---------------------- Products -------------------------------------------------------

class Product(BaseModel):
    id: int
    product: str  # This combines the name and vendor code

    class Config:
        from_attributes = True

@productorder_router.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    query = """
    SELECT 
        id,
        "name" || ' "' || vendor_code || '"' AS product 
    FROM product
    """
    try:
        result = db.execute(query).fetchall()
        return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------- Order Items by Product IDs -------------------------------------

class ProductIDs(BaseModel):
    product_ids: List[int]

class OrderItem(BaseModel):
    order_date: date
    order_number: int
    product: str
    stage: Optional[str]
    status: Optional[str]
    order_quantity: Optional[int]
    collected_quantity: Optional[int]
    order_type: Optional[str]

    class Config:
        from_attributes = True

@productorder_router.post("/order_items", response_model=List[OrderItem])
def get_order_items(product_ids: ProductIDs, db: Session = Depends(get_db)):
    query = text("""
        SELECT  
            CAST(o.created_on AS date) AS "order_date",
            oi.order_id AS "order_number",
            p."name" AS "product",
            ros."name" AS "stage",
            ros2."name" AS "status",
            oi.quantity AS "order_quantity",
            oi.sent_quantity AS "collected_quantity",
            CASE 
                WHEN o.dtype = 'RequestOrder' THEN 'заявка' 
                ELSE 'трансфер' 
            END AS "order_type" 
        FROM order_item oi 
        JOIN order_ o ON o.id = oi.order_id 
        JOIN public.ref_order_stage ros ON ros.id = o.stage_id 
        JOIN public.ref_order_status ros2 ON ros2.id = o.status_id 
        JOIN product p ON p.id = oi.product_id 
        WHERE oi.product_id IN :product_ids
                 order by oi.order_id
    """).bindparams(bindparam('product_ids', expanding=True))

    query_params = {'product_ids': product_ids.product_ids}

    try:
        result = db.execute(query, query_params).fetchall()
        return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
