import httpx
import logging
import traceback
from uuid import uuid4
from datetime import date, datetime
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8009")


def run_communication_event_crud_cycle():
    logger.info("Starting communication_event CRUD cycle test")
    communication_event_id = None
    status = {
        "create": False,
        "get": False,
        "update": False,
        "search": False,
        "delete": False,
        "verify_delete": False,
        "negative_get": False,
        "negative_update": False,
        "negative_delete": False
    }

    def build_payload():
        return {
        
            "conversation_id": "00000000-0000-0000-0000-000000000001",
        
            "workspace_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        
            "event_type": "email",
        
            "status": "sent",
        
            "occurred_at": "2025-09-16T02:35:34.102235+00:00",
        
            "created_at": "2025-09-16T02:35:34.102242+00:00",
        
            "created_by": "00000000-0000-0000-0000-000000000001",
        
        
            "sender_id": "00000000-0000-0000-0000-000000000001",
        
            "recipient_id": "00000000-0000-0000-0000-000000000001",
        
            "external_contact": "test_external_contact",
        
            "subject": "test_subject",
        
            "body": "test_body",
        
            "summary": "test_summary",
        
        }

    try:
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            try:
                # Create
                payload = build_payload()
                response = client.post("/", json=payload)
                logger.info("POST / -> status %d, response: %s", response.status_code, response.text)
                if response.status_code == 200:
                    status["create"] = True
                    created = response.json()
                    communication_event_id = created["id"]
                    logger.info("Created communication_event ID: %s", communication_event_id)
                else:
                    logger.error("Create failed with status %d: %s", response.status_code, response.text)
                    return 1

                # Get
                response = client.get(f"/{ communication_event_id }")
                logger.info("GET /%s -> status %d", communication_event_id, response.status_code)
                if response.status_code == 200:
                    status["get"] = True

                # Update
                update_payload = build_payload()
                response = client.put(f"/{ communication_event_id }", json=update_payload)
                logger.info("PUT /%s -> status %d", communication_event_id, response.status_code)
                if response.status_code == 200:
                    status["update"] = True

                # Search
                response = client.get("/")
                logger.info("GET / -> status %d", response.status_code)
                if response.status_code == 200 and any(item["id"] == communication_event_id for item in response.json()):
                    status["search"] = True

                # Negative: Get non-existent
                fake_id = str(uuid4())
                response = client.get(f"/{fake_id}")
                if response.status_code == 404:
                    status["negative_get"] = True

                # Negative: Update non-existent
                response = client.put(f"/{fake_id}", json=build_payload())
                if response.status_code == 404:
                    status["negative_update"] = True

                # Negative: Delete non-existent
                response = client.delete(f"/{fake_id}")
                if response.status_code == 404:
                    status["negative_delete"] = True

            finally:
                # Cleanup
                if communication_event_id:
                    try:
                        response = client.delete(f"/{ communication_event_id }")
                        if response.status_code == 200:
                            status["delete"] = True
                        response = client.get(f"/{ communication_event_id }")
                        if response.status_code == 404:
                            status["verify_delete"] = True
                    except Exception as e:
                        logger.warning("Error during cleanup: %s", e)

    except httpx.RequestError as e:
        logger.error("HTTP request error: %s", str(e))
        return 2
    except Exception as e:
        logger.error("Unexpected error:\n%s", traceback.format_exc())
        return 3

    logger.info("✅ Test Summary:")
    for step, success in status.items():
        emoji = "✅" if success else "❌"
        logger.info("%s %s", emoji, step.replace("_", " ").capitalize())

    if all(status.values()):
        logger.info("🎉 All communication_event tests passed successfully")
        return 0
    else:
        logger.error("❌ One or more communication_event tests failed")
        return 4


if __name__ == "__main__":
    sys.exit(run_communication_event_crud_cycle())
