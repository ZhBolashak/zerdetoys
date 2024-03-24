# sale_endpoint.py
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from backend.database import get_db
from sqlalchemy import func, text
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


sales_router = APIRouter()

class SaleOrder(BaseModel):
    days: date
    created_on: datetime
    transaction_id: int
    external_id:Optional[str]
    amount: float
    store: str
    payment: Optional[str]
    typ_states: Optional[str]
    typ_cash: Optional[str]
    currency: Optional[str]
    first_name: Optional[str]
    username: Optional[str]

    class Config:
        from_attributes = True

def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {date_str}")


@sales_router.post("/sales-and-orders/", response_model=List[SaleOrder])
def read_sales_and_orders(
    store: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    start_date_obj = parse_date(start_date) if start_date else None
    end_date_obj = parse_date(end_date) if end_date else None

    query_params = {'store': store, 'start_date': start_date_obj, 'end_date': end_date_obj}



    # Обновлённый запрос с учётом новой логики
    query = """
    SELECT * FROM (
                        
                    ---продажа 
                    select cast(s.created_on as date) days,
                    to_char(s.created_on ,'YYYY-MM-DD HH24:MI:SS') created_on,
                    s.id transaction_id,s.external_id ,sp.amount  ,
                    s2."name" store ,  rspt."name" payment,'постуление_касса' typ_states, 'продажа' typ_cash, 'тенге' currency, ua.first_name ,ua.username 
                    from sale s
                    join store s2 on s2.id =s.store_id 
                    join sale_payment sp on sp.sale_id =s.id 
                    join ref_sale_payment_type rspt on rspt.id =sp.payment_type_id 
                    left join user_account ua on ua.id =s.client_id 
                    where sp.amount>0
                    union 
                    ---заявки
                    select  cast(o.created_on as date), 
                    to_char(o.created_on,'YYYY-MM-DD HH24:MI:SS') , o.id order_id,null ,o.final_total_amount,
                    'Zerde' , ropt."name",'постуление_заявка' typ_states , 'заявка', 'тенге' currency, ua2.first_name ,ua2.username 
                    from order_ o
                    join ref_order_stage ros on ros.id =o.stage_id 
                    join ref_order_status ros2 on ros2.id =o.status_id 
                    join order_payment op on op.order_id =o.id 
                    join ref_order_payment_type ropt on ropt.id =op.payment_type_id 
                    left join user_account ua2 on ua2.id=o.client_id
                    where ros2.id ='COMPLETED' --and ropt.id =1 
                    and o.dtype ='RequestOrder' and final_total_amount>0
                    union 
                    select  cast(cf.created_on as date),
                    coalesce(to_char(CF.created_on,'YYYY-MM-DD HH:MI:SS'), to_char(cf.occurred_on ,'YYYY-MM-DD HH24:MI:SS')) , 
                    cf.id,null,
                    case when rpag.id in (2) then (-1)*amount else amount end amount--,rpag.id
                    , coalesce(s2."name",'Zerde') , rwt."name" ,rpa."name" , rpag."name", rc."name" , c.first_name ,c.username 
                    from cash_flow cf 
                    left join store s2 on s2.id =cf.store_id 
                    join public.ref_wallet_type rwt on rwt.id =cf.wallet_type_id 
                    join ref_payment_article rpa on cf.payment_article_id =rpa.id 
                    join ref_payment_article_group rpag on rpag.id=rpa.payment_article_group_id 
                    join ref_currency rc on rc.id =cf.currency_id 
                    left join user_account c on c.id =cf.client_id  
                    where rpa.id not in (1) and rpag.id not in (3)
                        )  as combined_results
    WHERE combined_results.store = :store AND combined_results.days >= :start_date AND combined_results.days <= :end_date
    ORDER BY combined_results.created_on
    """
    
    try:
        results = db.execute(query, query_params).fetchall()
        sale_orders = [SaleOrder(**dict(zip(result.keys(), result))) for result in results]
        logger.info("Запрос успешно обработан")
        return sale_orders
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



#----------------------Магазин список-------------------------------------------------------
class Store(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@sales_router.get("/store", response_model=List[Store])
def get_stores(db: Session = Depends(get_db)):
    try:
        # Выполнение запроса к базе данных
        store = db.execute("SELECT id, name FROM store").fetchall()
        # Преобразование результатов в список словарей
        return [{"id": id, "name": name} for id, name in store]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#----------------------Список cтатьей движения средств-------------------------------------------------------
class PaymentArticle(BaseModel):
    payment_article_group_id: int
    payment_article_group: str  
    payment_article_id: int
    ref_payment_article: str

    class Config:
        from_attributes = True

@sales_router.get("/payment_articles", response_model=List[PaymentArticle])
def get_payment_articles(db: Session = Depends(get_db)):
    try:
        articles = db.execute("""
            SELECT rpag.id AS payment_article_group_id,
                   rpag.name AS payment_article_group,
                   rpa.id AS payment_article_id,
                   rpa.name AS ref_payment_article
            FROM ref_payment_article rpa
            JOIN ref_payment_article_group rpag ON rpa.payment_article_group_id = rpag.id
            where rpa.is_system is not true  
        """).fetchall()

        # Преобразование результатов в список экземпляров PaymentArticle
        return [PaymentArticle(
                    payment_article_group_id=row['payment_article_group_id'],
                    payment_article_group=row['payment_article_group'],
                    payment_article_id=row['payment_article_id'],
                    ref_payment_article=row['ref_payment_article']
                ) for row in articles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    #----------------------список кошельков-------------------------------------------------------
class Wallet(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@sales_router.get("/wallet", response_model=List[Wallet])
def get_wallets(db: Session = Depends(get_db)):
    try:
        wallet = db.execute("select id,name  from ref_wallet_type rwt ").fetchall()
        return [{"id": id, "name": name} for id, name in wallet]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    #----------------------список валюты-------------------------------------------------------
class Currency(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@sales_router.get("/currency", response_model=List[Currency])
def get_currency(db: Session = Depends(get_db)):
    try:
        currency = db.execute("select id,name  from ref_currency").fetchall()
        return [{"id": id, "name": name} for id, name in currency]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#----------------------добавление данных в ДДС-------------------------------------------------------

class CashFlowCreate(BaseModel):
    amount: float
    client_id: Optional[int]
    currency_id: int
    payment_article_id: int
    wallet_type_id: int
    occurred_on: date
    store_id: int

@sales_router.post("/cash_flow")
def create_cash_flow(cash_flow_data: CashFlowCreate, db: Session = Depends(get_db)):
    try:
        # SQL выражение для INSERT
        insert_query = """
        INSERT INTO cash_flow (
            amount, 
            created_by, 
            created_on, 
            description, 
            client_id, 
            currency_id, 
            payment_article_id, 
            wallet_type_id, 
            occurred_on, 
            store_id, 
            occurred_month
        )
        VALUES (
            :amount, 
            null,
            CURRENT_DATE,
            null,
            :client_id,
            :currency_id,
            :payment_article_id,
            :wallet_type_id,
            :occurred_on,
            :store_id,
            (SELECT id FROM ref_month WHERE code=TO_CHAR(:occurred_on, 'MONTH'))
        )
        """
        # Привязанные параметры используют значения из cash_flow_data
        result = db.execute(insert_query, {
            'amount': cash_flow_data.amount,
            'client_id': cash_flow_data.client_id,
            'currency_id': cash_flow_data.currency_id,
            'payment_article_id': cash_flow_data.payment_article_id,
            'wallet_type_id': cash_flow_data.wallet_type_id,
            'occurred_on': cash_flow_data.occurred_on,
            'store_id': cash_flow_data.store_id
        })
        db.commit()
        return {"message": "Cash flow record created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
