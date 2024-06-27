#credit_endpoints.py
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from backend.database import get_db

credit_router = APIRouter()
#------------------------- получение указанных даннных--------------

class CashFlowcredit(BaseModel):
    id: int
    дата_формирования: date
    дата_посадки: date
    направление: Optional[str]
    сумма: Optional[float]
    валюта: Optional[str]
    кошелек: Optional[str]
    провайдер: Optional[str]

    class Config:
        from_attributes = True

@credit_router.get("/cash_flow_credit", response_model=List[CashFlowcredit])
def get_cash_flow(db: Session = Depends(get_db)):
    query = """
    SELECT cf.id,
        cast(cf.created_on as date) AS "дата_формирования",
        cast(cf.occurred_on as date) AS "дата_посадки",
        rpa."name"  AS "направление",
        case when payment_article_id in (38,22) then (-1)*cf.amount else cf.amount end  "сумма", 
        rc."name" AS "валюта",
        w."name" as "кошелек",
        p."name"  "провайдер"
    from cash_flow cf 
    left JOIN provider p on p.id=cf.provider_id
    join ref_wallet_type w on w.id =cf.wallet_type_id 
    join ref_payment_article rpa on rpa.id =cf.payment_article_id 
    join ref_currency rc on rc.id =cf.currency_id 
    where cf.payment_article_id in (23,36,39)
    order by cf.id desc 
    """

    try:
        result = db.execute(query).fetchall()
        return [dict(row) for row in result]
    except Exception as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))



#------------------------- получение статьей --------------

class PaymentArticlecredit(BaseModel):
    id: int
    ref_payment_article: str

    class Config:
        from_attributes = True

@credit_router.get("/payment_articles_credit", response_model=List[PaymentArticlecredit])
def get_payment_articles(db: Session = Depends(get_db)):
    try:
        articles = db.execute("""
            SELECT rpa.id,
                   rpa.name AS ref_payment_article
            FROM ref_payment_article rpa
            WHERE rpa.is_system IS NOT TRUE AND rpa.id IN (23,36,39)
        """).fetchall()

        # Преобразование результатов в список экземпляров PaymentArticle
        return [PaymentArticlecredit(id=row['id'], ref_payment_article=row['ref_payment_article']) for row in articles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#----------------------Провайдер-------------------------------------------------------
class Provider(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True

@credit_router.get("/provider", response_model=List[Provider])
def get_providers(db: Session = Depends(get_db)):
    try:
        # Выполнение запроса к базе данных
        providers = db.execute("SELECT id,name  FROM provider p ").fetchall()
        # Преобразование результатов в список словарей
        return [{"id": id, "name": name} for id, name in providers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
#----------------------добавление данных в ДДС-------------------------------------------------------

class CashFlowCreate(BaseModel):
    amount: float
    currency_id: int
    payment_article_id: int
    wallet_type_id: int
    occurred_on: date
    provider_id: int

@credit_router.post("/cash_flow_credit_insert")
def create_cash_flow(cash_flow_data: CashFlowCreate, db: Session = Depends(get_db)):
    try:
        # SQL выражение для INSERT
        insert_query = """
        INSERT INTO cash_flow (
            amount, 
            created_by, 
            created_on, 
            currency_id, 
            payment_article_id, 
            wallet_type_id, 
            occurred_on, 
            store_id, 
            provider_id,
            occurred_month
        )
        VALUES (
            :amount, 
            1,
            CURRENT_DATE,
            :currency_id,
            :payment_article_id,
            :wallet_type_id,
            :occurred_on,
            1,
            :provider_id,
            (SELECT id FROM ref_month WHERE code=TO_CHAR(:occurred_on, 'MONTH'))
        )
        """
        # Привязанные параметры используют значения из cash_flow_data
        result = db.execute(insert_query, {
            'amount': cash_flow_data.amount,
            'currency_id': cash_flow_data.currency_id,
            'payment_article_id': cash_flow_data.payment_article_id,
            'wallet_type_id': cash_flow_data.wallet_type_id,
            'occurred_on': cash_flow_data.occurred_on,
            'provider_id': cash_flow_data.provider_id
        })
        db.commit()
        return {"message": "Cash flow record created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
