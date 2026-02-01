from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.lead_priority import router as lead_router
from src.routers.call_eval import router as call_router


app = FastAPI(title="Fixit GenAI Assignment")


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


app.include_router(lead_router, prefix="/api/v1")
app.include_router(call_router, prefix="/api/v1")


@app.get("/")
def root():
	return {"status": "ok", "service": "fixit-genai"}