from uuid import UUID
from datetime import date
from app.models.transaction import Transaction
from app.shared.enums import TransactionPhase, TransactionStatus

def get_transaction_seed_data():
    return [
        Transaction(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            agent_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            location_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            buyer_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            seller_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            transaction_date=date(2025, 7, 1),
            sale_price=450000.00,
            commission_rate=0.03,
            phase=TransactionPhase.ACTIVE_LISTING,
            status=TransactionStatus.ACTIVE
        ),
        Transaction(
            id=UUID("11111111-1111-1111-1111-111111111112"),
            agent_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            location_id=UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"),
            buyer_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            seller_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            transaction_date=date(2025, 6, 15),
            sale_price=1500000.00,
            commission_rate=0.025,
            phase=TransactionPhase.UNDER_CONTRACT,
            status=TransactionStatus.ACTIVE
        ),
        Transaction(
            id=UUID("11111111-1111-1111-1111-111111111113"),
            agent_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            location_id=UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
            buyer_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            seller_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            transaction_date=date(2025, 5, 10),
            sale_price=320000.00,
            commission_rate=0.028,
            phase=TransactionPhase.CLOSED,
            status=TransactionStatus.COMPLETED
        ),
        Transaction(
            id=UUID("11111111-1111-1111-1111-111111111114"),
            agent_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            location_id=UUID("99999999-9999-9999-9999-999999999999"),
            buyer_id=None,
            seller_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            transaction_date=date(2025, 7, 20),
            sale_price=880000.00,
            commission_rate=0.03,
            phase=TransactionPhase.OFFER_RECEIVED,
            status=TransactionStatus.ACTIVE
        ),
        Transaction(
            id=UUID("11111111-1111-1111-1111-111111111115"),
            agent_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            location_id=UUID("00000000-0000-0000-0000-000000000001"),
            buyer_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            seller_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            transaction_date=date(2025, 4, 5),
            sale_price=2100000.00,
            commission_rate=0.027,
            phase=TransactionPhase.POST_CLOSING,
            status=TransactionStatus.COMPLETED
        )
    ]
