from uuid import UUID
from datetime import datetime
from app.models.workspace import Workspace

def get_workspace_seed_data():
    return [
        Workspace(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name="Acme Corp",
            slug="acme-corp",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 2, 12, 0, 0),
            created_by=UUID("11111111-1111-1111-1111-111111111111"),
            owner_id=UUID("22222222-2222-2222-2222-222222222222"),
            is_active=True
        ),
        Workspace(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            name="Globex Corporation",
            slug="globex-corporation",
            created_at=datetime(2024, 2, 1, 9, 30, 0),
            updated_at=datetime(2024, 2, 2, 10, 0, 0),
            created_by=UUID("33333333-3333-3333-3333-333333333333"),
            owner_id=UUID("44444444-4444-4444-4444-444444444444"),
            is_active=True
        ),
        Workspace(
            id=UUID("00000000-0000-0000-0000-000000000003"),
            name="Wayne Enterprises",
            slug="wayne-enterprises",
            created_at=datetime(2024, 3, 1, 8, 0, 0),
            updated_at=datetime(2024, 3, 2, 8, 30, 0),
            created_by=UUID("55555555-5555-5555-5555-555555555555"),
            owner_id=UUID("66666666-6666-6666-6666-666666666666"),
            is_active=False
        ),
        Workspace(
            id=UUID("00000000-0000-0000-0000-000000000004"),
            name="Stark Industries",
            slug="stark-industries",
            created_at=datetime(2024, 4, 1, 14, 0, 0),
            updated_at=datetime(2024, 4, 2, 15, 0, 0),
            created_by=UUID("77777777-7777-7777-7777-777777777777"),
            owner_id=UUID("88888888-8888-8888-8888-888888888888"),
            is_active=True
        ),
        Workspace(
            id=UUID("00000000-0000-0000-0000-000000000005"),
            name="Oscorp",
            slug="oscorp",
            created_at=datetime(2024, 5, 1, 16, 0, 0),
            updated_at=datetime(2024, 5, 2, 17, 0, 0),
            created_by=UUID("99999999-9999-9999-9999-999999999999"),
            owner_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            is_active=True
        )
    ]

class HumanCreate(WorkspaceUserBase):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None