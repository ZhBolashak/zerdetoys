from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from backend.database import get_db, Session

app = FastAPI()
costs_router = APIRouter()

# Модель данных для денежного потока
class CashFlowInfo(BaseModel):
    id: int
    дата: date
    Направление: Optional[str]
    Расход: float
    Валюта: Optional[str]
    кошелек: Optional[str]
    Группа: Optional[str]
    Тип: Optional[str]

    class Config:
        from_attributes = True

@costs_router.get("/cash_flow_costs", response_model=List[CashFlowInfo])
def get_cash_flow(db: Session = Depends(get_db)):
    query = """
    SELECT 
        cf.id,
        cast(cf.created_on as date) AS "дата",
        rpa."name" AS "Направление",
        cf.amount AS "Расход",
        rc."name" AS "Валюта",
        rwt."name" AS "кошелек",
        rpag."name" AS "Группа",
        rpal."name" AS "Тип"
    FROM cash_flow cf 
    JOIN ref_payment_article rpa ON rpa.id = cf.payment_article_id 
    JOIN ref_payment_article_group rpag ON rpag.id = rpa.payment_article_group_id 
    JOIN ref_payment_article_line rpal ON rpal.id = rpa.payment_article_line_id 
    JOIN ref_wallet_type rwt ON cf.wallet_type_id = rwt.id 
    JOIN ref_currency rc ON rc.id = cf.currency_id 
    WHERE cf.payment_article_id NOT IN (1,22,23,24,28,36,38,39) 
    AND rpa.is_system IS NOT true
    """

    try:
        result = db.execute(query).fetchall()
        return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#----------------------Магазин список-------------------------------------------------------
class Store(BaseModel):
    id: int
    name: Optional[str]  

    class Config:
        from_attributes = True


@costs_router.get("/store_costs", response_model=List[Store])
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

@costs_router.get("/payment_articles_costs", response_model=List[PaymentArticle])
def get_payment_articles(db: Session = Depends(get_db)):
    try:
        articles = db.execute("""
            SELECT rpag.id AS payment_article_group_id,
                   rpag.name AS payment_article_group,
                   rpa.id AS payment_article_id,
                   rpa.name AS ref_payment_article
            FROM ref_payment_article rpa
            JOIN ref_payment_article_group rpag ON rpa.payment_article_group_id = rpag.id
            where rpa.id not in (1,22,23,24,28,36,38,39) and rpa.is_system is not true  
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


@costs_router.get("/wallet_costs", response_model=List[Wallet])
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


@costs_router.get("/currency_costs", response_model=List[Currency])
def get_currency(db: Session = Depends(get_db)):
    try:
        currency = db.execute("select id,name  from ref_currency").fetchall()
        return [{"id": id, "name": name} for id, name in currency]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#----------------------добавление данных в ДДС-------------------------------------------------------

class CashFlowCreate(BaseModel):
    amount: float
    currency_id: int
    payment_article_id: int
    wallet_type_id: int
    occurred_on: date
    store_id: int

@costs_router.post("/cash_flow_costs_insert")
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
            :store_id,
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
            'store_id': cash_flow_data.store_id
        })
        db.commit()
        return {"message": "Cash flow record created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
