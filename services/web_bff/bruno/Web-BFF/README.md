# Web-BFF Bruno API Collection

This Bruno collection provides comprehensive API testing for the web-bff service endpoints. The service runs on `http://localhost:8050` as configured in docker-compose.yml.

## 📁 Collection Structure

### 🏥 Health Check

- **Health Check** - `GET /health` - Service health status

### 🔐 Account Setup

Initial user registration and email activation flow:

- **Signup (Self)** - `POST /account-setup/signup` - Self-signup without workspace
- **Signup (Workspace Invite)** - `POST /account-setup/signup` - Signup with workspace invitation
- **Confirm Email** - `POST /account-setup/confirm` - Activate email with confirmation code
- **Check Status** - `GET /account-setup/status/{email}` - Check signup status
- **List All Emails (Admin)** - `GET /account-setup/emails` - Admin endpoint for all signups
- **Get Email by Code** - `GET /account-setup/email-for-code/{code}` - Lookup email by activation code

### 👤 User Setup

Complete user profile setup after email activation:

- **Complete User Setup (Join Workspace)** - `POST /user-setup/complete` - Join existing workspace
- **Complete User Setup (Create Workspace)** - `POST /user-setup/complete` - Create new workspace
- **Validate Workspace** - `GET /user-setup/workspaces/{id}/validate` - Validate workspace for signup

### 🏢 Workspaces

Workspace management endpoints:

- **Search Workspaces** - `GET /workspaces` - Search and list workspaces with filters
- **Create Workspace** - `POST /workspaces` - Create new workspace
- **Validate Workspace for Signup** - `GET /workspaces/{id}/validate` - Validate workspace accessibility

### 🔑 Authentication

User authentication and session management:

- **Login** - `POST /auth/login` - User login with email/password
- **Validate Session** - `GET /auth/validate` - Validate current session
- **Logout** - `POST /auth/logout` - End user session

### 👥 Human Directory

Human records management (CRUD operations):

- **Create Human** - `POST /views/directory` - Create single human record
- **Bulk Create Humans** - `POST /views/directory/bulk` - Create multiple human records
- **Get Humans** - `GET /views/directory` - List humans with filters and pagination
- **Get Single Human** - `GET /views/directory/{id}` - Get specific human record
- **Update Human** - `PATCH /views/directory/{id}` - Update single human record
- **Bulk Update Humans** - `PATCH /views/directory/bulk` - Update multiple human records
- **Delete Human** - `DELETE /views/directory/{id}` - Delete single human record
- **Bulk Delete Humans** - `DELETE /views/directory/bulk` - Delete multiple human records

## 🚀 Getting Started

1. **Start the service**: Ensure docker containers are running

   ```bash
   docker-compose up -d
   ```

2. **Verify service**: Use the Health Check endpoint first

   ```
   GET http://localhost:8050/health
   ```

3. **Test user flow**: Follow the typical user signup flow:
   - Account Setup → Signup
   - Account Setup → Confirm Email
   - User Setup → Complete User Setup
   - Authentication → Login

## 📝 Notes

- **Port**: Service runs on `localhost:8050` (mapped from container port 8000)
- **Authentication**: Most endpoints use session-based auth with cookies
- **UUIDs**: Example UUIDs are provided for testing (replace with actual values)
- **Error Handling**: All endpoints include comprehensive error responses
- **Rollback**: User setup includes automatic rollback on failures

## 🔧 Environment Variables

The collection uses these default values:

- **Base URL**: `http://localhost:8050`
- **Workspace ID**: `12345` (example)
- **User ID**: `00000000-0000-0000-0000-000000000001` (example UUID)

## 📚 API Documentation

Interactive Swagger documentation is available at:
`http://localhost:8050/docs`

This provides detailed schema information, example requests/responses, and the ability to test endpoints directly from the browser.
