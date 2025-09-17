def get_tables():
    return {
        "location": {
            "port": 8002,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "name", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "address_line1", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "address_line2", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "city", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "state", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "USState", "enum_type": "USState"},
                {"name": "postal_code", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "country", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "latitude", "required": False, "sqlalchemy_type": "Float", "pydantic_type": "float"},
                {"name": "longitude", "required": False, "sqlalchemy_type": "Float", "pydantic_type": "float"},
                {"name": "location_type", "required": True, "sqlalchemy_type": "String", "pydantic_type": "LocationType", "enum_type": "LocationType"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
        "transaction": {
            "port": 8003,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "agent_id", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "location_id", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "buyer_id", "required": False, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "seller_id", "required": False, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "transaction_date", "required": True, "sqlalchemy_type": "Date", "pydantic_type": "date"},
                {"name": "sale_price", "required": True, "sqlalchemy_type": "Float", "pydantic_type": "float"},
                {"name": "commission_rate", "required": True, "sqlalchemy_type": "Float", "pydantic_type": "float"},
                {"name": "phase", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "TransactionPhase", "enum_type": "TransactionPhase"},
                {"name": "status", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "TransactionStatus", "enum_type": "TransactionStatus"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
        "human": {
            "port": 8004,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "first_name", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "last_name", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "middle_name", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "email", "required": False, "sqlalchemy_type": "String", "pydantic_type": "EmailStr"},
                {"name": "phone_number", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "linkedin_url", "required": False, "sqlalchemy_type": "String", "pydantic_type": "HttpUrl"},
                {"name": "created_at", "required": False, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "updated_at", "required": False, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
        "workspace": {
            "port": 8005,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "Integer", "pydantic_type": "int", "autoincrement": True},
                {"name": "name", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "created_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "updated_at", "required": False, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "owner_id", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "is_active", "required": False, "sqlalchemy_type": "Boolean", "pydantic_type": "bool", "default": True},
            ]
        },
        "workspace_member": {
            "port": 8006,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "role", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "invited_by", "required": False, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "joined_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "is_active", "required": True, "sqlalchemy_type": "Boolean", "pydantic_type": "bool"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
        "workspace_invite": {
            "port": 8007,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "email", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "invited_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "role", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "invite_token", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "created_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "expires_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "accepted_at", "required": False, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
        "conversation": {
            "port": 8008,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "topic", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "conversation_type", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "ConversationType", "enum_type": "ConversationType"},
                {"name": "summary", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "created_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "updated_at", "required": False, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"}
            ]
        },
        "communication_event": {
            "port": 8009,
            "fields": [
                {"name": "id", "required": True, "primary_key": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "conversation_id", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "workspace_id", "required": True, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "sender_id", "required": False, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "recipient_id", "required": False, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
                {"name": "external_contact", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "event_type", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "CommunicationEventType", "enum_type": "CommunicationEventType"},
                {"name": "subject", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "body", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "status", "required": True, "sqlalchemy_type": "Enum", "pydantic_type": "CommunicationStatus", "enum_type": "CommunicationStatus"},
                {"name": "summary", "required": False, "sqlalchemy_type": "String", "pydantic_type": "str"},
                {"name": "occurred_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "created_at", "required": True, "sqlalchemy_type": "DateTime", "pydantic_type": "datetime"},
                {"name": "created_by", "required": True, "sqlalchemy_type": "UUID", "pydantic_type": "UUID"},
            ]
        },
    }