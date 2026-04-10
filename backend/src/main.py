from fastapi import FastAPI

from src.routers import profiles, teams, join_requests

app = FastAPI(
    title="Hackathon Team Finder",
    description=(
        "API for finding and forming hackathon teams "
        "at Innopolis University."
    ),
    version="0.1.0",
)

app.include_router(profiles.router)
app.include_router(teams.router)
app.include_router(join_requests.router)
