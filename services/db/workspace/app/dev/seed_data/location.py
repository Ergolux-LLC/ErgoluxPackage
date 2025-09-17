from uuid import UUID
from app.models.location import Location
from app.shared.enums import USState, CountryCode

def get_location_seed_data():
    return [
        Location(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name="Graceland",
            address_line1="3764 Elvis Presley Blvd",
            address_line2="",
            city="Memphis",
            state=USState.TN,
            postal_code="38116",
            country=CountryCode.USA,
            latitude=35.0456,
            longitude=-90.0220
        ),
        Location(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            name="Neverland Ranch",
            address_line1="5225 Figueroa Mountain Rd",
            address_line2="",
            city="Los Olivos",
            state=USState.CA,
            postal_code="93441",
            country=CountryCode.USA,
            latitude=34.7361,
            longitude=-120.0888
        ),
        Location(
            id=UUID("00000000-0000-0000-0000-000000000003"),
            name="Oprah Winfrey's Montecito Estate",
            address_line1="1633 E Valley Rd",
            address_line2="",
            city="Montecito",
            state=USState.CA,
            postal_code="93108",
            country=CountryCode.USA,
            latitude=34.4401,
            longitude=-119.6322
        ),
        Location(
            id=UUID("00000000-0000-0000-0000-000000000004"),
            name="Drake's Toronto Mansion",
            address_line1="21 Park Lane Circle",
            address_line2="",
            city="Toronto",
            state="ON",  # Not in USState enum
            postal_code="M3B 1Z8",
            country=CountryCode.CANADA,
            latitude=43.7476,
            longitude=-79.3635
        ),
        Location(
            id=UUID("00000000-0000-0000-0000-000000000005"),
            name="Taylor Swift's Rhode Island House",
            address_line1="16 Bluff Avenue",
            address_line2="",
            city="Westerly",
            state=USState.RI,
            postal_code="02891",
            country=CountryCode.USA,
            latitude=41.3204,
            longitude=-71.8052
        )
    ]
