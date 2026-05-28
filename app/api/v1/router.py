from fastapi import APIRouter

from app.api.v1.endpoints.animals import router as animals_router
from app.api.v1.endpoints.animal_events import router as animal_events_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.expenses import router as expenses_router
from app.api.v1.endpoints.financials import router as financials_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.income import router as income_router
from app.api.v1.endpoints.milk_entries import router as milk_entries_router


api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(animals_router, tags=["Animals"])
api_router.include_router(animal_events_router, tags=["Animal Events"])
api_router.include_router(dashboard_router, tags=["Dashboard"])
api_router.include_router(expenses_router, tags=["Expenses"])
api_router.include_router(financials_router, tags=["Financials"])
api_router.include_router(income_router, tags=["Income"])
api_router.include_router(milk_entries_router, tags=["Milk Entries"])
