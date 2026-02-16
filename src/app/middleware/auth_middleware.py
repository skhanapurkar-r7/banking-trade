"""Authentication and Authorization Middleware.

This middleware handles JWT token validation and access control.
Currently disabled (pass-through) but includes commented implementation for future use.
"""

from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Uncomment when implementing authentication
# from jose import JWTError, jwt
# from datetime import datetime
# from app.core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication and Authorization Middleware.

    Validates JWT tokens and enforces access control policies.
    Currently configured as pass-through (no validation).

    Supports:
    - JWT token validation
    - RBAC (Role-Based Access Control)
    - ABAC (Attribute-Based Access Control)
    """

    def __init__(self, app, secret_key: str = "your-secret-key", algorithm: str = "HS256"):
        """
        Initialize authentication middleware.

        Args:
            app: FastAPI application instance
            secret_key: Secret key for JWT validation
            algorithm: JWT algorithm (default: HS256)
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm

        # Public endpoints that don't require authentication
        self.public_endpoints = [
            "/",
            "/health",
            "/health/db",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request through authentication and authorization.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response: HTTP response
        """
        # Currently: Pass-through mode (no authentication)
        # Uncomment the implementation below when ready to enable authentication

        response = await call_next(request)
        return response

        # ============================================================================
        # IMPLEMENTATION: Uncomment below to enable authentication
        # ============================================================================

        # # Skip authentication for public endpoints
        # if self._is_public_endpoint(request.url.path):
        #     response = await call_next(request)
        #     return response

        # # Extract token from Authorization header
        # token = self._extract_token(request)
        # if not token:
        #     return Response(
        #         content='{"detail": "Missing authentication token"}',
        #         status_code=401,
        #         media_type="application/json"
        #     )

        # # Validate JWT token
        # try:
        #     payload = self._validate_token(token)
        #
        #     # Add user info to request state for downstream use
        #     request.state.user_id = payload.get("sub")
        #     request.state.username = payload.get("username")
        #     request.state.email = payload.get("email")
        #     request.state.role = payload.get("role", "user")
        #     request.state.permissions = payload.get("permissions", [])
        #
        # except JWTError as e:
        #     return Response(
        #         content=f'{{"detail": "Invalid token: {str(e)}"}}',
        #         status_code=401,
        #         media_type="application/json"
        #     )
        # except Exception as e:
        #     return Response(
        #         content=f'{{"detail": "Authentication error: {str(e)}"}}',
        #         status_code=401,
        #         media_type="application/json"
        #     )

        # # Authorization: Check access control
        # if not self._check_authorization(request):
        #     return Response(
        #         content='{"detail": "Insufficient permissions"}',
        #         status_code=403,
        #         media_type="application/json"
        #     )

        # # Proceed to next middleware/endpoint
        # response = await call_next(request)
        # return response

    def _is_public_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is public (no authentication required).

        Args:
            path: Request path

        Returns:
            bool: True if public endpoint
        """
        return any(path.startswith(endpoint) for endpoint in self.public_endpoints)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Supports:
        - Bearer token: "Authorization: Bearer <token>"
        - Custom header: "X-API-Token: <token>"

        Args:
            request: HTTP request

        Returns:
            Optional[str]: JWT token or None
        """
        # Method 1: Bearer token (standard)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        # Method 2: Custom header (alternative)
        api_token = request.headers.get("X-API-Token")
        if api_token:
            return api_token

        # Method 3: Cookie (for web applications)
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            return token_cookie

        return None

    def _validate_token(self, token: str) -> dict:
        """
        Validate JWT token and extract payload.

        Validates:
        - Token signature
        - Token expiration
        - Token format

        Args:
            token: JWT token string

        Returns:
            dict: Token payload

        Raises:
            JWTError: If token is invalid
        """
        # Uncomment when implementing
        # try:
        #     # Decode and validate token
        #     payload = jwt.decode(
        #         token,
        #         self.secret_key,
        #         algorithms=[self.algorithm]
        #     )
        #
        #     # Check expiration
        #     exp = payload.get("exp")
        #     if exp and datetime.utcnow().timestamp() > exp:
        #         raise JWTError("Token has expired")
        #
        #     # Validate required fields
        #     if not payload.get("sub"):
        #         raise JWTError("Token missing subject (user ID)")
        #
        #     return payload
        #
        # except JWTError as e:
        #     raise e
        # except Exception as e:
        #     raise JWTError(f"Token validation failed: {str(e)}")

        pass

    def _check_authorization(self, request: Request) -> bool:
        """
        Check if user is authorized to access the endpoint.

        Implements both RBAC and ABAC access control strategies.

        Args:
            request: HTTP request with user info in state

        Returns:
            bool: True if authorized
        """
        # Get user info from request state (set during authentication)
        # user_role = request.state.role
        # user_permissions = request.state.permissions
        # user_id = request.state.user_id

        # Get request details
        # method = request.method
        # path = request.url.path

        # ============================================================================
        # RBAC (Role-Based Access Control)
        # ============================================================================
        # Use when: Access is primarily determined by user roles
        # Example: Admin, Manager, User, Guest
        #
        # Pros:
        # - Simple to implement and understand
        # - Easy to manage (assign roles to users)
        # - Good for hierarchical organizations
        # - Scales well for most applications
        #
        # Cons:
        # - Less flexible for complex scenarios
        # - Role explosion (too many roles)
        # - Hard to handle exceptions
        #
        # Implementation:
        # if self._check_rbac(user_role, method, path):
        #     return True

        # ============================================================================
        # ABAC (Attribute-Based Access Control)
        # ============================================================================
        # Use when: Access depends on multiple attributes/conditions
        # Example: User attributes, resource attributes, environment attributes
        #
        # Pros:
        # - Very flexible and fine-grained
        # - Handles complex scenarios
        # - Dynamic access decisions
        # - Supports context-aware access
        #
        # Cons:
        # - More complex to implement
        # - Harder to debug and audit
        # - Performance overhead
        # - Requires policy engine
        #
        # Implementation:
        # if self._check_abac(request):
        #     return True

        # Default: Allow all (when authentication is disabled)
        return True

    def _check_rbac(self, role: str, method: str, path: str) -> bool:
        """
        Role-Based Access Control (RBAC) implementation.

        Define access rules based on user roles.

        Args:
            role: User role (admin, manager, user, guest)
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Request path

        Returns:
            bool: True if authorized

        Example Rules:
            - Admin: Full access to all endpoints
            - Manager: Read/Write trades, Read-only users
            - User: Read/Write own trades, Read-only others
            - Guest: Read-only access
        """
        # Define role hierarchy (higher roles inherit lower role permissions)
        # role_hierarchy = {
        #     "admin": ["admin", "manager", "user", "guest"],
        #     "manager": ["manager", "user", "guest"],
        #     "user": ["user", "guest"],
        #     "guest": ["guest"]
        # }

        # Define access rules
        # access_rules = {
        #     # Admin: Full access
        #     "admin": {
        #         "GET": ["*"],
        #         "POST": ["*"],
        #         "PUT": ["*"],
        #         "DELETE": ["*"]
        #     },
        #
        #     # Manager: Read/Write trades, no delete
        #     "manager": {
        #         "GET": ["/api/v1/trades*", "/api/v1/users*"],
        #         "POST": ["/api/v1/trades*"],
        #         "PUT": ["/api/v1/trades*"],
        #         "DELETE": []
        #     },
        #
        #     # User: Read/Write own trades
        #     "user": {
        #         "GET": ["/api/v1/trades*"],
        #         "POST": ["/api/v1/trades*"],
        #         "PUT": ["/api/v1/trades*"],  # Additional check: own trades only
        #         "DELETE": []
        #     },
        #
        #     # Guest: Read-only
        #     "guest": {
        #         "GET": ["/api/v1/trades*"],
        #         "POST": [],
        #         "PUT": [],
        #         "DELETE": []
        #     }
        # }

        # # Check if role has permission for this method and path
        # if role not in access_rules:
        #     return False

        # allowed_paths = access_rules[role].get(method, [])

        # # Check wildcard access
        # if "*" in allowed_paths:
        #     return True

        # # Check specific path patterns
        # for pattern in allowed_paths:
        #     if pattern.endswith("*"):
        #         if path.startswith(pattern[:-1]):
        #             return True
        #     elif path == pattern:
        #         return True

        # return False

        pass

    def _check_abac(self, request: Request) -> bool:
        """
        Attribute-Based Access Control (ABAC) implementation.

        Make access decisions based on multiple attributes:
        - User attributes (role, department, clearance level)
        - Resource attributes (owner, classification, status)
        - Environment attributes (time, location, IP address)
        - Action attributes (read, write, delete)

        Args:
            request: HTTP request with user and resource info

        Returns:
            bool: True if authorized

        Example Policies:
            1. Users can only modify their own trades
            2. Managers can modify trades in their department
            3. Trades can only be deleted during business hours
            4. Expired trades cannot be modified
            5. High-value trades require manager approval
        """
        # Extract attributes
        # user_attrs = {
        #     "user_id": request.state.user_id,
        #     "role": request.state.role,
        #     "department": request.state.get("department"),
        #     "clearance_level": request.state.get("clearance_level", 0)
        # }

        # resource_attrs = self._get_resource_attributes(request)

        # env_attrs = {
        #     "time": datetime.utcnow(),
        #     "ip_address": request.client.host,
        #     "user_agent": request.headers.get("user-agent")
        # }

        # action = request.method

        # # Define policies
        # policies = [
        #     self._policy_own_resource(user_attrs, resource_attrs, action),
        #     self._policy_department_access(user_attrs, resource_attrs, action),
        #     self._policy_business_hours(env_attrs, action),
        #     self._policy_resource_status(resource_attrs, action),
        #     self._policy_value_threshold(user_attrs, resource_attrs, action)
        # ]

        # # All policies must pass (AND logic)
        # # Or use OR logic depending on requirements
        # return all(policies)

        pass

    def _get_resource_attributes(self, request: Request) -> dict:
        """
        Extract resource attributes from request.

        Args:
            request: HTTP request

        Returns:
            dict: Resource attributes
        """
        # # Extract resource ID from path
        # path_parts = request.url.path.split("/")
        # resource_id = None
        #
        # if len(path_parts) > 4 and path_parts[3] == "trades":
        #     try:
        #         resource_id = int(path_parts[4])
        #     except (ValueError, IndexError):
        #         pass
        #
        # # Fetch resource from database
        # if resource_id:
        #     # from app.repositories.trade_repository import TradeRepository
        #     # trade = repository.get_by_id(resource_id)
        #     # return {
        #     #     "owner_id": trade.created_by,
        #     #     "department": trade.department,
        #     #     "status": "expired" if trade.expired else "active",
        #     #     "value": trade.value,
        #     #     "classification": trade.classification
        #     # }
        #     pass

        return {}

    # ============================================================================
    # ABAC Policy Examples
    # ============================================================================

    def _policy_own_resource(self, user_attrs: dict, resource_attrs: dict, action: str) -> bool:
        """
        Policy: Users can only modify their own resources.

        Exception: Admins and managers can modify any resource.
        """
        # if action in ["PUT", "DELETE"]:
        #     # Admins and managers bypass this policy
        #     if user_attrs["role"] in ["admin", "manager"]:
        #         return True
        #
        #     # Users can only modify their own resources
        #     return user_attrs["user_id"] == resource_attrs.get("owner_id")
        #
        # # Read operations allowed for all
        # return True

        return True

    def _policy_department_access(
        self, user_attrs: dict, resource_attrs: dict, action: str
    ) -> bool:
        """
        Policy: Users can only access resources in their department.

        Exception: Admins have cross-department access.
        """
        # if user_attrs["role"] == "admin":
        #     return True
        #
        # return user_attrs["department"] == resource_attrs.get("department")

        return True

    def _policy_business_hours(self, env_attrs: dict, action: str) -> bool:
        """
        Policy: Destructive operations only allowed during business hours.

        Business hours: Monday-Friday, 9 AM - 5 PM UTC
        """
        # if action == "DELETE":
        #     current_time = env_attrs["time"]
        #
        #     # Check if weekday (0 = Monday, 6 = Sunday)
        #     if current_time.weekday() >= 5:  # Weekend
        #         return False
        #
        #     # Check if business hours (9 AM - 5 PM)
        #     if current_time.hour < 9 or current_time.hour >= 17:
        #         return False
        #
        # return True

        return True

    def _policy_resource_status(self, resource_attrs: dict, action: str) -> bool:
        """
        Policy: Expired resources cannot be modified.
        """
        # if action in ["PUT", "DELETE"]:
        #     if resource_attrs.get("status") == "expired":
        #         return False
        #
        # return True

        return True

    def _policy_value_threshold(self, user_attrs: dict, resource_attrs: dict, action: str) -> bool:
        """
        Policy: High-value trades require manager approval.

        High-value: > $1,000,000
        """
        # if action in ["POST", "PUT"]:
        #     value = resource_attrs.get("value", 0)
        #
        #     # High-value trades require manager or admin role
        #     if value > 1_000_000:
        #         return user_attrs["role"] in ["admin", "manager"]
        #
        # return True

        return True


# ============================================================================
# Usage in FastAPI Application
# ============================================================================

# # In src/app/main.py:
# from app.middleware.auth_middleware import AuthMiddleware
#
# app.add_middleware(
#     AuthMiddleware,
#     secret_key=settings.secret_key,
#     algorithm="HS256"
# )

# ============================================================================
# Accessing User Info in Endpoints
# ============================================================================

# # In your endpoint handlers:
# @router.get("/trades")
# def list_trades(request: Request):
#     # Access authenticated user info
#     user_id = request.state.user_id
#     username = request.state.username
#     role = request.state.role
#     permissions = request.state.permissions
#
#     # Use user info for business logic
#     if role == "user":
#         # Filter trades by user
#         trades = service.get_user_trades(user_id)
#     else:
#         # Return all trades
#         trades = service.get_all_trades()
#
#     return trades
