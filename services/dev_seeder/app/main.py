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
                
                # Try to find and delete existing human records through web-BFF
                # Search for humans in any workspace created by this user
                try:
                    human_search_response = await client.get(
                        f"{WEB_BFF_URL}/views/directory?created_by={user_id}&limit=100",
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
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up human records: {str(e)}")
                
                # Find existing workspaces through web-BFF (search by user_id if supported)
                try:
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
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up workspaces: {str(e)}")
                
                logger.info("✅ Cleanup completed through web-BFF")
            else:
                logger.info("ℹ️ No existing user found, skipping cleanup")
                
    except Exception as e:
        logger.error(f"⚠️ Error during cleanup (continuing anyway): {str(e)}")

async def register_dev_user():
    """Register the development user through web-BFF account setup and user setup endpoints"""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Try to login first to see if user already exists
            login_response = await client.post(
                f"{WEB_BFF_URL}/auth/login",
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                # User already exists and can login
                login_data = login_response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("access_token")
                logger.info("ℹ️ Developer user already exists and logged in successfully through web-BFF")
                logger.info(f"✅ User ID: {user_id}")
                return user_id, access_token
            
            # Step 2: User doesn't exist, start account setup process through web-BFF
            logger.info("👤 Creating new developer user through web-BFF account setup...")
            
            # Step 2a: Signup through web-BFF account setup
            signup_response = await client.post(
                f"{WEB_BFF_URL}/account-setup/signup",
                json={"email": dev_user["email"]}
            )
            
            if signup_response.status_code != 200:
                logger.error(f"❌ Account setup signup failed: {signup_response.text}")
                return None, None
            
            signup_data = signup_response.json()
            if not signup_data.get("success"):
                logger.error(f"❌ Account setup signup failed: {signup_data.get('reason')}")
                return None, None
            
            logger.info("✅ Account setup signup successful through web-BFF")
            
            # Step 2b: Get the activation code (dev mode only)
            import urllib.parse
            encoded_email = urllib.parse.quote(dev_user["email"], safe='')
            code_response = await client.get(
                f"{WEB_BFF_URL}/account-setup/dev/get-code/{encoded_email}"
            )
            
            if code_response.status_code != 200:
                logger.error(f"❌ Failed to get activation code: {code_response.text}")
                return None, None
            
            code_data = code_response.json()
            activation_code = code_data.get("code")
            if not activation_code:
                logger.error("❌ No activation code returned")
                return None, None
            
            logger.info(f"✅ Got activation code: {activation_code}")
            
            # Step 2c: Confirm the activation code through web-BFF
            confirm_response = await client.post(
                f"{WEB_BFF_URL}/account-setup/confirm",
                json={"code": activation_code}
            )
            
            if confirm_response.status_code != 200:
                logger.error(f"❌ Code confirmation failed: {confirm_response.text}")
                return None, None
            
            confirm_data = confirm_response.json()
            if not confirm_data.get("valid"):
                logger.error("❌ Activation code is invalid")
                return None, None
            
            logger.info("✅ Activation code confirmed through web-BFF")
            
            # Step 2d: Complete user setup through web-BFF user setup
            user_setup_data = {
                "first_name": "Dev",
                "last_name": "User",
                "email": dev_user["email"],
                "password": dev_user["password"],
                "new_workspace_name": "Dev Workspace"
            }
            
            setup_response = await client.post(
                f"{WEB_BFF_URL}/user-setup/complete",
                json=user_setup_data
            )
            
            if setup_response.status_code != 200:
                logger.error(f"❌ User setup completion failed: {setup_response.text}")
                return None, None
            
            setup_data = setup_response.json()
            if not setup_data.get("success"):
                logger.error(f"❌ User setup failed: {setup_data.get('error_details')}")
                return None, None
            
            user_id = setup_data.get("user_id")
            access_token = setup_data.get("access_token")
            workspace_id = setup_data.get("workspace_id")
            
            logger.info("✅ Developer user created and set up successfully through web-BFF")
            logger.info(f"✅ User ID: {user_id}")
            logger.info(f"✅ Workspace ID: {workspace_id}")
            
            return user_id, access_token
                
    except Exception as e:
        logger.error(f"❌ Error with developer user setup through web-BFF: {str(e)}")
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
    
    # Step 2: Register/login user through web-BFF (includes workspace creation)
    user_id, access_token = await register_dev_user()
    if not user_id or not access_token:
        logger.error("❌ Failed to setup developer user through web-BFF")
        return
    
    # Get workspace info by searching for workspaces owned by this user
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    cookies = {"user_id": user_id}
    
    try:
        async with httpx.AsyncClient() as client:
            workspace_search_response = await client.get(
                f"{WEB_BFF_URL}/workspaces?limit=10",
                headers=headers,
                cookies=cookies
            )
            
            workspace_id = None
            if workspace_search_response.status_code == 200:
                workspace_data = workspace_search_response.json()
                if workspace_data.get("results"):
                    # Get the most recent workspace
                    workspace_id = workspace_data["results"][-1].get("id")
                    logger.info(f"🏢 Found created workspace: {workspace_id}")
    except Exception as e:
        logger.warning(f"⚠️ Could not retrieve workspace ID: {str(e)}")
        workspace_id = "unknown"
    
    # Step 3: Create human record through web-BFF
    human_id = await create_dev_human(access_token, user_id, workspace_id)
    if not human_id:
        logger.error("❌ Failed to create human record through web-BFF")
        return
    
    # Step 4: Verify complete login flow through web-BFF
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