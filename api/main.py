from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import trends, compare, inflation, basket

app = FastAPI(
    title="SA Grocery Price Intelligence API",
    description="Analytics API for SA grocery price tracking",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trends.router, prefix="/trends", tags=["trends"])
app.include_router(compare.router, prefix="/compare", tags=["compare"])
app.include_router(inflation.router, prefix="/inflation", tags=["inflation"])
app.include_router(basket.router, prefix="/basket", tags=["basket"])


@app.get("/health")
def health():
    return {"status": "ok"}