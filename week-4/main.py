import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in the .env file"
    )


# ============================================================
# SUPABASE CLIENT
# ============================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FlyRank Week 4 - Auth API",
    description="Authentication API using FastAPI and Supabase",
    version="1.0.0",
)


# ============================================================
# SWAGGER BEARER AUTHENTICATION
# ============================================================

security = HTTPBearer(auto_error=False)


# ============================================================
# REQUEST MODEL
# ============================================================

class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None


# ============================================================
# AUTHENTICATION DEPENDENCY
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    # No Authorization header
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Must use Bearer authentication
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Verify JWT using Supabase
    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        return {
            "user": response.user,
            "token": token
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ============================================================
# HOME ROUTE
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Server running and connected to Supabase"
    }


# ============================================================
# STAGE 1 - SIGNUP
# ============================================================

@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthRequest):

    # Missing fields
    if (
        not credentials.email
        or not credentials.password
        or not credentials.email.strip()
        or not credentials.password.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email.strip(),
            "password": credentials.password
        })

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Unable to create user"
            )

        return {
            "message": "User created successfully",
            "user": response.user
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# STAGE 1 - LOGIN
# ============================================================

@app.post("/auth/login")
def login(credentials: AuthRequest):

    # Missing fields
    if (
        not credentials.email
        or not credentials.password
        or not credentials.email.strip()
        or not credentials.password.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email.strip(),
            "password": credentials.password
        })

        if response.session is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid login credentials"
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )


# ============================================================
# STAGE 2 - PUBLIC ROUTE
# ============================================================

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# ============================================================
# STAGE 3 / 4 - PROTECTED PROFILE
# ============================================================

@app.get("/protected/profile")
def protected_profile(
    auth_data=Depends(get_current_user)
):
    user = auth_data["user"]

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# ============================================================
# STAGE 4 - PROTECTED DASHBOARD
# ============================================================

@app.get("/protected/dashboard")
def protected_dashboard(
    auth_data=Depends(get_current_user)
):
    user = auth_data["user"]

    return {
        "message": "Welcome to the protected dashboard",
        "user_id": user.id,
        "email": user.email
    }


# ============================================================
# STAGE 4 - LOGOUT
# ============================================================

@app.post("/auth/logout", status_code=204)
def logout(
    auth_data=Depends(get_current_user)
):
    try:
        supabase.auth.sign_out()

        return Response(
            status_code=204
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Logout failed"
        )