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

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8004")


def run_human_crud_cycle():
    logger.info("Starting human CRUD cycle test")
    human_id = None
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
        
            "workspace_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        
            "first_name": "test_first_name",
        
            "last_name": "test_last_name",
        
            "created_by": "00000000-0000-0000-0000-000000000001",
        
        
            "middle_name": "test_middle_name",
        
            "email": "unknown_email",
        
            "phone_number": "test_phone_number",
        
            "linkedin_url": "unknown_linkedin_url",
        
            "created_at": "2025-09-16T02:35:34.075671+00:00",
        
            "updated_at": "2025-09-16T02:35:34.075960+00:00",
        
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
                    human_id = created["id"]
                    logger.info("Created human ID: %s", human_id)
                else:
                    logger.error("Create failed with status %d: %s", response.status_code, response.text)
                    return 1

                # Get
                response = client.get(f"/{ human_id }")
                logger.info("GET /%s -> status %d", human_id, response.status_code)
                if response.status_code == 200:
                    status["get"] = True

                # Update
                update_payload = build_payload()
                response = client.put(f"/{ human_id }", json=update_payload)
                logger.info("PUT /%s -> status %d", human_id, response.status_code)
                if response.status_code == 200:
                    status["update"] = True

                # Search
                response = client.get("/")
                logger.info("GET / -> status %d", response.status_code)
                if response.status_code == 200 and any(item["id"] == human_id for item in response.json()):
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
                if human_id:
                    try:
                        response = client.delete(f"/{ human_id }")
                        if response.status_code == 200:
                            status["delete"] = True
                        response = client.get(f"/{ human_id }")
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
        logger.info("🎉 All human tests passed successfully")
        return 0
    else:
        logger.error("❌ One or more human tests failed")
        return 4


if __name__ == "__main__":
    sys.exit(run_human_crud_cycle())
