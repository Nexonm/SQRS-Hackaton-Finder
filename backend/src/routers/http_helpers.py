"""Small helpers to keep routers compact and consistent."""

from fastapi import HTTPException, Response, status


def require_resource(resource, detail: str):
    if resource is None:
        raise HTTPException(status_code=404, detail=detail)
    return resource


def no_content_or_404(deleted: bool, detail: str) -> Response:
    if not deleted:
        raise HTTPException(status_code=404, detail=detail)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
