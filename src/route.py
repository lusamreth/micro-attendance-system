from fastapi import APIRouter

attd_router = APIRouter(prefix="/attendance")
# attd_router.

from .db import init_db_root

init_db_root()


@attd_router.get("/")
def list_names():
    pass


@attd_router.get("/{id}")
def list_name_single():
    pass
