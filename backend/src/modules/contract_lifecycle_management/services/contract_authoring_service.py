"""
Contract Authoring & Milestone Lifecycle Service.
"""
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import ContractDocument, ContractMilestoneBilling
from ..schemas import ContractDocumentCreate

class ContractAuthoringService:
    @staticmethod
    async def create_contract(
        session: AsyncSession,
        payload: ContractDocumentCreate,
        tenant_id: str,
        actor_id: str
    ) -> ContractDocument:
        contract = ContractDocument(
            tenant_id=tenant_id,
            contract_number=payload.contract_number,
            title=payload.title,
            contract_type=payload.contract_type,
            status="DRAFT_AUTHORING",
            counterparty_name=payload.counterparty_name,
            counterparty_signatory_email=payload.counterparty_signatory_email,
            internal_owner_user_id=actor_id,
            effective_date=payload.effective_date,
            expiration_date=payload.expiration_date,
            renewal_type=payload.renewal_type,
            renewal_notice_days=payload.renewal_notice_days,
            total_contract_value=payload.total_contract_value,
            governing_law_jurisdiction=payload.governing_law_jurisdiction
        )
        session.add(contract)
        await session.flush()

        for ms in payload.milestones:
            m_rec = ContractMilestoneBilling(
                tenant_id=tenant_id,
                contract_id=contract.id,
                milestone_name=ms.milestone_name,
                milestone_percentage=ms.milestone_percentage,
                billing_amount=ms.billing_amount,
                target_delivery_date=ms.target_delivery_date,
                is_deliverable_accepted=False
            )
            session.add(m_rec)

        await session.commit()
        await session.refresh(contract)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_CONTRACT",
            entity_type="ContractDocument",
            entity_id=contract.id,
            description=f"Created contract #{payload.contract_number} with {payload.counterparty_name}"
        )
        return contract
