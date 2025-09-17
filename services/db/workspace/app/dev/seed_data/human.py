from uuid import UUID
from datetime import datetime
from app.models.human import Human

def get_human_seed_data():
    return [
        Human(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Kingsley",
            last_name="Shacklebolt",
            middle_name=None,
            email="kingsley.shacklebolt@ministry.gov.uk",
            phone_number="+442079876543",
            linkedin_url="https://www.linkedin.com/in/kingsleyshacklebolt",
            created_at=datetime(2022, 7, 1, 10, 0, 0),
            updated_at=datetime(2022, 7, 2, 12, 0, 0),
            created_by=UUID("11111111-1111-1111-1111-111111111111")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Emmeline",
            last_name="Vance",
            middle_name=None,
            email="emmeline.vance@order.org",
            phone_number="+442079876544",
            linkedin_url="https://www.linkedin.com/in/emmelinevance",
            created_at=datetime(2022, 8, 1, 9, 30, 0),
            updated_at=datetime(2022, 8, 2, 11, 0, 0),
            created_by=UUID("11111111-1111-1111-1111-111111111111")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000003"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Sturgis",
            last_name="Podmore",
            middle_name=None,
            email="sturgis.podmore@order.org",
            phone_number="+442079876545",
            linkedin_url="https://www.linkedin.com/in/sturgispodmore",
            created_at=datetime(2022, 9, 1, 8, 0, 0),
            updated_at=datetime(2022, 9, 2, 10, 0, 0),
            created_by=UUID("22222222-2222-2222-2222-222222222222")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000004"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Hestia",
            last_name="Jones",
            middle_name=None,
            email="hestia.jones@order.org",
            phone_number="+442079876546",
            linkedin_url="https://www.linkedin.com/in/hestiajones",
            created_at=datetime(2022, 10, 1, 7, 0, 0),
            updated_at=datetime(2022, 10, 2, 9, 0, 0),
            created_by=UUID("22222222-2222-2222-2222-222222222222")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000005"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Dedalus",
            last_name="Diggle",
            middle_name=None,
            email="dedalus.diggle@order.org",
            phone_number="+442079876547",
            linkedin_url="https://www.linkedin.com/in/dedalusdiggle",
            created_at=datetime(2022, 11, 1, 6, 0, 0),
            updated_at=datetime(2022, 11, 2, 8, 0, 0),
            created_by=UUID("33333333-3333-3333-3333-333333333333")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000006"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Arabella",
            last_name="Figg",
            middle_name="Doreen",
            email="arabella.figg@catlover.uk",
            phone_number="+442079876548",
            linkedin_url="https://www.linkedin.com/in/arabelladfigg",
            created_at=datetime(2022, 12, 1, 5, 0, 0),
            updated_at=datetime(2022, 12, 2, 7, 0, 0),
            created_by=UUID("33333333-3333-3333-3333-333333333333")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000007"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Elphias",
            last_name="Doge",
            middle_name=None,
            email="elphias.doge@wizengamot.org",
            phone_number="+442079876549",
            linkedin_url="https://www.linkedin.com/in/elphiasdoge",
            created_at=datetime(2023, 1, 1, 4, 0, 0),
            updated_at=datetime(2023, 1, 2, 6, 0, 0),
            created_by=UUID("44444444-4444-4444-4444-444444444444")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000008"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Mundungus",
            last_name="Fletcher",
            middle_name=None,
            email="mundungus.fletcher@order.org",
            phone_number="+442079876550",
            linkedin_url="https://www.linkedin.com/in/mundungusfletcher",
            created_at=datetime(2023, 2, 1, 3, 0, 0),
            updated_at=datetime(2023, 2, 2, 5, 0, 0),
            created_by=UUID("44444444-4444-4444-4444-444444444444")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000009"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Marietta",
            last_name="Edgecombe",
            middle_name=None,
            email="marietta.edgecombe@ministry.gov.uk",
            phone_number="+442079876551",
            linkedin_url="https://www.linkedin.com/in/mariettaedgecombe",
            created_at=datetime(2023, 3, 1, 2, 0, 0),
            updated_at=datetime(2023, 3, 2, 4, 0, 0),
            created_by=UUID("55555555-5555-5555-5555-555555555555")
        ),
        Human(
            id=UUID("00000000-0000-0000-0000-000000000010"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Charity",
            last_name="Burbage",
            middle_name=None,
            email="charity.burbage@hogwarts.edu.uk",
            phone_number="+442079876552",
            linkedin_url="https://www.linkedin.com/in/charityburbage",
            created_at=datetime(2023, 4, 1, 1, 0, 0),
            updated_at=datetime(2023, 4, 2, 3, 0, 0),
            created_by=UUID("55555555-5555-5555-5555-555555555555")
        ),
        Human(
            id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            workspace_id=UUID("b7e6a8c2-1f2d-4e3a-9b5c-2a1e4f6c7d8e"),
            first_name="Dev",
            last_name="User",
            middle_name=None,
            email="dev.user@example.com",
            phone_number="+10000000000",
            linkedin_url="https://www.linkedin.com/in/devuser",
            created_at=datetime(2023, 8, 1, 12, 0, 0),
            updated_at=datetime(2023, 8, 2, 13, 0, 0),
            created_by=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")  # or your actual dev user UUID
        )
    ]