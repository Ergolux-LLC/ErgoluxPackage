import asyncio
import logging
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s"
)

logger = logging.getLogger(__name__)

async def create_and_login_dev_user():
    """Create and login developer user through web-BFF"""
    logger.info("👤 Creating and logging in developer user...")
    
    # Use web-BFF as the API gateway
    web_bff_url = "http://web_bff:8000"
    
    dev_user = {
        "email": "dev@example.com",
        "password": "devpassword123",
        "first_name": "Dev",
        "last_name": "User"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Try to login first (in case user already exists)
            login_url = f"{web_bff_url}/auth/login"
            
            response = await client.post(
                login_url,
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                login_data = response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("access_token")
                logger.info(f"✅ Developer user logged in successfully (ID: {user_id})")
                return user_id, access_token
            
            elif response.status_code == 401:
                # User doesn't exist, try to register through auth service directly
                logger.info("👤 User doesn't exist, creating through auth service...")
                return await register_dev_user()
            
            else:
                logger.error(f"❌ Login failed with status {response.status_code}: {response.text}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Error logging in developer user: {str(e)}")
            return None, None

async def register_dev_user():
    """Register user through auth service and then login through web-BFF"""
    auth_url = "http://auth_service:8000"
    web_bff_url = "http://web_bff:8000"
    
    dev_user = {
        "email": "dev@example.com",
        "password": "devpassword123",
        "first_name": "Dev",
        "last_name": "User"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Try to register through auth service
            register_url = f"{auth_url}/register"
            
            response = await client.post(
                register_url,
                data=dev_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                logger.info("✅ Developer user registered successfully")
            elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
                logger.info("ℹ️ Developer user already exists (using existing)")
            else:
                logger.error(f"❌ Registration failed with status {response.status_code}: {response.text}")
                return None, None
            
            # Now login through auth service to get tokens
            login_url = f"{auth_url}/login"
            
            login_response = await client.post(
                login_url,
                data={"email": dev_user["email"], "password": dev_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("tokens", {}).get("access_token")
                logger.info(f"✅ Developer user logged in successfully (ID: {user_id})")
                return user_id, access_token
            else:
                logger.error(f"❌ Login failed: {login_response.text}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Error with developer user: {str(e)}")
            return None, None

async def create_dev_workspace(access_token, user_id):
    """Create a workspace through web-BFF (when workspace endpoints are available)"""
    logger.info("🏢 Creating developer workspace...")
    
    # For now, create directly since web-BFF might not have workspace endpoints yet
    # TODO: Update this when workspace endpoints are added to web-BFF
    workspace_url = "http://workspace_service:8000"
    
    workspace_data = {
        "name": "Dev Workspace",
        "created_at": datetime.now().isoformat(),
        "created_by": user_id,
        "owner_id": user_id,
        "is_active": True
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            create_url = f"{workspace_url}/"
            
            response = await client.post(
                create_url,
                json=workspace_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code == 200:
                workspace_data = response.json()
                workspace_id = workspace_data.get("id")
                logger.info(f"✅ Developer workspace created: {workspace_data.get('name')} (ID: {workspace_id})")
                return workspace_id
            else:
                logger.error(f"❌ Workspace creation failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating developer workspace: {str(e)}")
            return None

async def create_dev_human(access_token, user_id, workspace_id):
    """Create a human record through web-BFF (when human endpoints are available)"""
    logger.info("👨‍💼 Creating developer human record...")
    
    # For now, create directly since web-BFF might not have human endpoints yet
    # TODO: Update this when human endpoints are added to web-BFF
    human_url = "http://human_service:8000"
    
    human_data = {
        "workspace_id": str(workspace_id),
        "first_name": "Dev",
        "last_name": "User",
        "email": "dev@example.com",
        "created_by": user_id
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            create_url = f"{human_url}/"
            
            response = await client.post(
                create_url,
                json=human_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code == 200:
                human_data = response.json()
                human_id = human_data.get("id")
                logger.info(f"✅ Developer human created: {human_data.get('first_name')} {human_data.get('last_name')} (ID: {human_id})")
                return human_id
            else:
                logger.error(f"❌ Human creation failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating developer human: {str(e)}")
            return None

async def cleanup_existing_data():
    """Clean up any existing dev data before seeding"""
    logger.info("🧹 Cleaning up existing dev data...")
    
    dev_email = "dev@example.com"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # First, try to login to get user info if user exists
            auth_url = "http://auth_service:8000"
            login_response = await client.post(
                f"{auth_url}/login",
                data={"email": dev_email, "password": "devpassword123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                user_data = login_response.json()
                user_id = user_data.get("user", {}).get("id")
                logger.info(f"🔍 Found existing user: {user_id}")
                
                # Clean up human records with this email
                await cleanup_human_records(client, dev_email)
                
                # Clean up workspaces owned by this user
                await cleanup_workspaces(client, user_id)
                
                logger.info("✅ Cleanup completed")
            else:
                logger.info("ℹ️ No existing user found, skipping cleanup")
                
        except Exception as e:
            logger.warning(f"⚠️ Cleanup encountered error (continuing anyway): {str(e)}")

async def cleanup_human_records(client, email):
    """Remove human records with the dev email"""
    try:
        human_url = "http://human_service:8000"
        
        # Search for humans with this email
        search_response = await client.get(f"{human_url}/?email={email}")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            humans = search_data.get("results", [])
            
            for human in humans:
                human_id = human.get("id")
                if human_id:
                    delete_response = await client.delete(f"{human_url}/{human_id}")
                    if delete_response.status_code == 200:
                        logger.info(f"🗑️ Deleted human record: {human_id}")
                    else:
                        logger.warning(f"⚠️ Failed to delete human {human_id}: {delete_response.status_code}")
        
    except Exception as e:
        logger.warning(f"⚠️ Error cleaning up human records: {str(e)}")

async def cleanup_workspaces(client, user_id):
    """Remove workspaces owned by the user"""
    try:
        workspace_url = "http://workspace_service:8000"
        
        # Search for workspaces owned by this user
        search_response = await client.get(f"{workspace_url}/?owner_id={user_id}")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            workspaces = search_data.get("results", [])
            
            for workspace in workspaces:
                workspace_id = workspace.get("id")
                if workspace_id:
                    delete_response = await client.delete(f"{workspace_url}/{workspace_id}")
                    if delete_response.status_code == 200:
                        logger.info(f"🗑️ Deleted workspace: {workspace_id}")
                    else:
                        logger.warning(f"⚠️ Failed to delete workspace {workspace_id}: {delete_response.status_code}")
        
    except Exception as e:
        logger.warning(f"⚠️ Error cleaning up workspaces: {str(e)}")

async def main():
    """Main entry point"""
    logger.info("🌱 Development Seeder - Clean and Create Dev Setup")
    
    # Step 0: Clean up existing data
    await cleanup_existing_data()
    
    # Step 1: Register user through auth service if needed
    user_id, access_token = await register_dev_user()
    if not user_id:
        logger.error("❌ Failed to create developer user")
        exit(1)
    
    # Step 2: Create dev workspace directly (web-BFF doesn't have workspace endpoints yet)
    workspace_id = await create_dev_workspace(access_token, user_id)
    if not workspace_id:
        logger.error("❌ Failed to create developer workspace")
        exit(1)
    
    # Step 3: Create dev human directly (web-BFF doesn't have human endpoints yet)
    human_id = await create_dev_human(access_token, user_id, workspace_id)
    if not human_id:
        logger.error("❌ Failed to create developer human")
        exit(1)
    
    # Step 4: Now test web-BFF login (should work since human record exists)
    logger.info("🔍 Verifying web-BFF login works with complete setup...")
    web_bff_user_id, web_bff_token = await test_web_bff_login()
    if web_bff_user_id:
        logger.info(f"✅ Web-BFF login verification successful (ID: {web_bff_user_id})")
    else:
        logger.warning("⚠️ Web-BFF login verification failed, but core setup is complete")
    
    logger.info("✅ Seeding completed successfully")
    logger.info("📊 Created:")
    logger.info(f"  - User ID: {user_id}")
    logger.info(f"  - Workspace ID: {workspace_id}")
    logger.info(f"  - Human ID: {human_id}")
    if access_token:
        logger.info(f"  - Direct Auth Token: {access_token[:20]}...")

async def test_web_bff_login():
    """Test that web-BFF login works now that all records exist"""
    web_bff_url = "http://web_bff:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            login_url = f"{web_bff_url}/auth/login"
            
            response = await client.post(
                login_url,
                data={"email": "dev@example.com", "password": "devpassword123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                login_data = response.json()
                user_id = login_data.get("user", {}).get("id")
                access_token = login_data.get("access_token")
                return user_id, access_token
            else:
                logger.error(f"❌ Web-BFF login test failed: {response.status_code} - {response.text}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Error testing web-BFF login: {str(e)}")
            return None, None

if __name__ == "__main__":
    asyncio.run(main())