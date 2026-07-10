"""
Entrypoint for the backend API. Run with:
    uvicorn main:app --reload

This file should stay pure wiring -- no query logic, no business logic.
If you're tempted to write a SQL query here, it belongs in db.py; if
you're tempted to add an endpoint here, it belongs in routes/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import crimes, boroughs

app = FastAPI(title="Alfred API", description="NYC crime dashboard backend")

# Allows your frontend (running on a different port/domain during dev,
# e.g. localhost:5173) to actually call this API from the browser.
# Tighten allow_origins to your real frontend domain before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(crimes.router)
app.include_router(boroughs.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "alfred-api"}