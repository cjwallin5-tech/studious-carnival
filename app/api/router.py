from fastapi import APIRouter

from app.api.routes import admin, auth, comments, graph, posts, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
api_router.include_router(graph.router)
api_router.include_router(admin.router)
