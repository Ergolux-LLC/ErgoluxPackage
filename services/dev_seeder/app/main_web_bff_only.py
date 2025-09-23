import asyncio
import httpx
import logging
import os
from typing import Optional, Dict, Any

# Configure logging
os.makedirs("/app/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/app/logs/dev_seeder.log")
    ]
)

logger = logging.getLogger(__name__)

# Configuration
dev_user = {
    "email": "dev@example.com",
    "password": "devpassword123"
}

# Web-BFF is the single point of entry for all operations
WEB_BFF_URL = "http://web_bff:8000"

async def cleanup_existing_data():
    """Clean up existing dev data before creating new records using web-BFF only"""
    logger.info("🧹 Cleaning up existing dev data through web-BFF...")
    
    try:
        # First, try to login through web-BFF to see if user exists
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                f"{WEB_BFF_URL}/auth/login",
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                # User exists, get user ID and auth info
                login_data = login_response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("access_token")
                logger.info(f"🔍 Found existing user: {user_id}")
                
                # Set up authenticated headers and cookies for web-BFF
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                cookies = {"user_id": user_id}
                
                # Find and delete existing human records through web-BFF
                human_search_response = await client.get(
                    f"{WEB_BFF_URL}/views/directory?email={dev_user['email']}&limit=100",
                    headers=headers
                )
                
                if human_search_response.status_code == 200:
                    human_data = human_search_response.json()
                    if human_data.get("results"):
                        for human in human_data["results"]:
                            human_id = human.get("id")
                            delete_payload = {
                                "workspace_id": human.get("workspace_id"),
                                "created_by": user_id
                            }
                            delete_response = await client.request(
                                "DELETE",
                                f"{WEB_BFF_URL}/views/directory/{human_id}",
                                json=delete_payload,
                                headers=headers
                            )
                            if delete_response.status_code == 200:
                                logger.info(f"🗑️ Deleted human record: {human_id}")
                
                # Find existing workspaces through web-BFF (search by user_id if supported)
                workspace_search_response = await client.get(
                    f"{WEB_BFF_URL}/workspaces?limit=100",
                    headers=headers,
                    cookies=cookies
                )
                
                if workspace_search_response.status_code == 200:
                    workspace_data = workspace_search_response.json()
                    if workspace_data.get("results"):
                        for workspace in workspace_data["results"]:
                            workspace_id = workspace.get("id")
                            # Note: web-BFF doesn't have delete workspace endpoint yet
                            # This would need to be added to web-BFF for complete cleanup
                            logger.info(f"🗑️ Found workspace to clean: {workspace_id} (deletion not yet supported in web-BFF)")
                
                logger.info("✅ Cleanup completed through web-BFF")
            else:
                logger.info("ℹ️ No existing user found, skipping cleanup")
                
    except Exception as e:
        logger.error(f"⚠️ Error during cleanup (continuing anyway): {str(e)}")

async def register_dev_user():
    """Register or login the development user through web-BFF only"""
    try:
        async with httpx.AsyncClient() as client:
            # Try to register first through web-BFF
            register_response = await client.post(
                f"{WEB_BFF_URL}/auth/register",
                data=dev_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if register_response.status_code == 201:
                # Registration successful through web-BFF
                logger.info("✅ Developer user registered successfully through web-BFF")
            elif register_response.status_code == 400:
                # User already exists, that's fine
                logger.info("ℹ️ Developer user already exists (using existing)")
            else:
                logger.error(f"❌ Registration failed: {register_response.text}")
                return None, None
            
            # Now login through web-BFF to get tokens
            login_response = await client.post(
                f"{WEB_BFF_URL}/auth/login",
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("access_token")
                logger.info(f"✅ Developer user logged in successfully through web-BFF (ID: {user_id})")
                return user_id, access_token
            else:
                logger.error(f"❌ Login failed: {login_response.text}")
                return None, None
                
    except Exception as e:
        logger.error(f"❌ Error with developer user: {str(e)}")
        return None, None

async def create_dev_workspace(access_token, user_id):
    """Create a workspace through web-BFF only"""
    logger.info("🏢 Creating developer workspace through web-BFF...")
    
    workspace_data = {
        "name": "Dev Workspace"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Set user_id cookie for web-BFF
    cookies = {"user_id": user_id}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WEB_BFF_URL}/workspaces",
                json=workspace_data,
                headers=headers,
                cookies=cookies
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    workspace_id = response_data.get("workspace_id")
                    logger.info(f"✅ Developer workspace created through web-BFF: Dev Workspace (ID: {workspace_id})")
                    return workspace_id
                else:
                    logger.error(f"❌ Workspace creation failed: {response_data.get('reason')}")
                    return None
            else:
                logger.error(f"❌ Workspace creation failed with status {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Error creating developer workspace: {str(e)}")
        return None

async def create_dev_human(access_token, user_id, workspace_id):
    """Create a human record through web-BFF only"""
    logger.info("👨‍💼 Creating developer human record through web-BFF...")
    
    human_data = {
        "workspace_id": str(workspace_id),
        "first_name": "Dev",
        "last_name": "User", 
        "email": "dev@example.com",
        "created_by": user_id
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WEB_BFF_URL}/views/directory",
                json=human_data,
                headers=headers
            )
            
            if response.status_code == 200:
                human_response = response.json()
                human_id = human_response.get("id")
                logger.info(f"✅ Developer human created through web-BFF: Dev User (ID: {human_id})")
                return human_id
            else:
                logger.error(f"❌ Human creation failed with status {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Error creating developer human: {str(e)}")
        return None

async def test_web_bff_login(access_token):
    """Test that the complete web-BFF login flow works with all the created data"""
    logger.info("🔍 Verifying web-BFF login works with complete setup...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test the complete login flow through web-BFF
            response = await client.post(
                f"{WEB_BFF_URL}/auth/login",
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                login_data = response.json()
                user_id = login_data.get("user", {}).get("id")
                logger.info(f"✅ Web-BFF login verification successful through web-BFF (ID: {user_id})")
                return True
            else:
                logger.error(f"❌ Web-BFF login test failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error testing web-BFF login: {str(e)}")
        return False

async def main():
    """Main seeder function - creates complete dev environment through web-BFF only"""
    logger.info("🌱 Development Seeder - Clean and Create Dev Setup (WEB-BFF ONLY)")
    
    # Step 1: Clean up existing data through web-BFF
    await cleanup_existing_data()
    
    # Step 2: Register/login user through web-BFF
    user_id, access_token = await register_dev_user()
    if not user_id or not access_token:
        logger.error("❌ Failed to setup developer user through web-BFF")
        return
    
    # Step 3: Create workspace through web-BFF
    workspace_id = await create_dev_workspace(access_token, user_id)
    if not workspace_id:
        logger.error("❌ Failed to create workspace through web-BFF")
        return
    
    # Step 4: Create human record through web-BFF
    human_id = await create_dev_human(access_token, user_id, workspace_id)
    if not human_id:
        logger.error("❌ Failed to create human record through web-BFF")
        return
    
    # Step 5: Verify complete login flow through web-BFF
    login_success = await test_web_bff_login(access_token)
    if not login_success:
        logger.warning("⚠️ Web-BFF login verification failed, but core setup is complete")
    
    logger.info("✅ Seeding completed successfully through web-BFF")
    logger.info("📊 Created:")
    logger.info(f"  - User ID: {user_id}")
    logger.info(f"  - Workspace ID: {workspace_id}")
    logger.info(f"  - Human ID: {human_id}")
    logger.info(f"  - Direct Auth Token: {access_token[:20]}...")

if __name__ == "__main__":
    asyncio.run(main())