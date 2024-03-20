#debt_endpoint
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.database import get_db

debt_router = APIRouter()

class DebtOrder(BaseModel):
    data: date
    document: str
    Debet: Optional[float]
    Kredit: Optional[float]
    currency: Optional[str]
    first_name: Optional[str]

    class Config:
        from_attributes = True

def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {date_str}")

@debt_router.post("/debt/", response_model=List[DebtOrder])
def read_debt_orders(
    client: Optional[str] = None,  
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    start_date_obj = parse_date(start_date) if start_date else None
    end_date_obj = parse_date(end_date) if end_date else None

    client_filter = "AND f.first_name = :client" if client else ""
    date_filter = "AND f.data >= :start_date AND f.data <= :end_date" if start_date_obj and end_date_obj else ""

    query = f"""
       select *
from 
(SELECT 
    cast(s.created_on as date) AS "data",  -- вместо "datas"
    'Продажа кассой - № чека ' || COALESCE(s.external_id, s.id::text) AS "document",  -- вместо "documents"
    s.total_amount AS "Debet",
    NULL AS "Kredit",  -- вместо 'null "Кредит"'
    'тенге' AS "currency",
    ua.first_name || '-' || ua.username AS "first_name"  -- убедитесь, что это поле соответствует типу данных модели
FROM sale s 
JOIN user_account ua ON ua.id = s.client_id
union all
select 
    cast(s.created_on as date) AS days,
   'Оплата кассой - № чека ' || COALESCE(s.external_id, s.id::text) AS enumber,
   null "Дебет", sp.amount "Кредит",
    'тенге' AS currency,
    first_name || '-' || username
   from sale s 
   JOIN user_account ua ON ua.id = s.client_id
   join sale_payment sp on sp.sale_id =s.id 
   where sp.payment_type_id not in (3) --and ua.first_name = 'Жамбыл '
union all   
SELECT 
    cast(o.created_on as date) AS days,
    'Продажа заявки - № ' || o.id::text AS enumber,
    o.final_total_amount  "Дебет", null "Кредит",
    'тенге' AS currency,
    first_name || '-' || username
from order_ o 
JOIN user_account ua ON ua.id = o.client_id
WHERE o.status_id ='COMPLETED' 
union all
SELECT 
    cast(o.created_on as date) AS days,
    'Оплата заявки - № ' || o.id::text AS enumber,
    null "Дебет", op.amount "Кредит",
    'тенге' AS currency,
    first_name || '-' || username
from order_ o 
join order_payment op on o.id =op.order_id 
JOIN user_account ua ON ua.id = o.client_id
WHERE o.status_id ='COMPLETED' and op.payment_type_id =1 
union all
SELECT 
    cast(cf.created_on as date) AS days,
    rpa."name"  AS enumber,
    cf.amount  "Дебет", null "Кредит",
    rc."name" AS currency,
    first_name || '-' || username
from cash_flow cf 
JOIN user_account ua ON ua.id = cf.client_id
join ref_payment_article rpa on rpa.id =cf.payment_article_id 
join ref_currency rc on rc.id =cf.currency_id 
where cf.payment_article_id=28 
union all
SELECT 
    cast(cf.created_on as date) AS days,
    rpa."name"  AS enumber,
    null  "Дебет", cf.amount  "Кредит",
    rc."name" AS currency,
    first_name || '-' || username
from cash_flow cf 
JOIN user_account ua ON ua.id = cf.client_id
join ref_payment_article rpa on rpa.id =cf.payment_article_id 
join ref_currency rc on rc.id =cf.currency_id 
where cf.payment_article_id=24
)f
        WHERE 1=1
        {client_filter}
        {date_filter}
        ORDER BY f.data
    """

    query_params = {'client': client, 'start_date': start_date_obj, 'end_date': end_date_obj}

    try:
        results = db.execute(query, query_params).fetchall()
        debt_orders = [DebtOrder(**dict(row)) for row in results]
        return debt_orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





#----------------------Провайдер-------------------------------------------------------
class Clients(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True

@debt_router.get("/clients", response_model=List[Clients])
def get_providers(db: Session = Depends(get_db)):
    try:
        # Выполнение запроса к базе данных
        providers = db.execute("SELECT id,first_name || '-' || username AS user_identity FROM user_account ua").fetchall()
        # Преобразование результатов в список словарей
        return [{"id": id, "name": name} for id, name in providers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
