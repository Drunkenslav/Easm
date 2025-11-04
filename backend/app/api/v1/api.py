"""
Main API router that includes all endpoint routers
"""
from fastapi import APIRouter

# from app.api.v1.endpoints import auth, scans, assets, vulnerabilities, users

api_router = APIRouter()

# Include endpoint routers
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
# api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
# api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["vulnerabilities"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])

@api_router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {"message": "EASM Platform API v1"}
