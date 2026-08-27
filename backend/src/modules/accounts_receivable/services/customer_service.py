"""
NexERP Customer Master & Credit Limit Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.accounts_receivable.models import Customer
from backend.src.modules.accounts_receivable.schemas import CustomerCreate, CustomerUpdate


class CustomerService:
    """
    Customer accounts directory and credit risk manager.
    """

    @classmethod
    async def create_customer(cls, db: AsyncSession, tenant_id: str, payload: CustomerCreate) -> Customer:
        query = select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.customer_number == payload.customer_number.strip(),
            Customer.is_deleted == False
        )
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Customer with number '{payload.customer_number}' already exists.")

        customer = Customer(
            tenant_id=tenant_id,
            customer_number=payload.customer_number.strip(),
            name=payload.name.strip(),
            tax_identifier=payload.tax_identifier,
            customer_group=payload.customer_group,
            payment_terms_days=payload.payment_terms_days,
            credit_limit=payload.credit_limit,
            credit_hold=payload.credit_hold,
            currency=payload.currency.upper(),
            email=payload.email,
            phone=payload.phone,
            billing_address=payload.billing_address,
            shipping_address=payload.shipping_address,
            ar_account_id=payload.ar_account_id,
            revenue_account_id=payload.revenue_account_id
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @classmethod
    async def get_customer(cls, db: AsyncSession, tenant_id: str, customer_id: str) -> Optional[Customer]:
        query = select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_customers(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        query = (
            select(Customer)
            .where(Customer.tenant_id == tenant_id, Customer.is_deleted == False)
            .order_by(Customer.name.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
