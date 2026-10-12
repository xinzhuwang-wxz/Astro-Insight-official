# Add these imports to api_service/main.py

from api_service.llm_routes import router as llm_router
from api_service.stream_routes import router as stream_router

# Register after app creation:
#
# app.include_router(llm_router)
# app.include_router(stream_router)