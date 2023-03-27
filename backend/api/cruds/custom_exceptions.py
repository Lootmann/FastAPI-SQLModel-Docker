from fastapi import HTTPException, status


class AuthException:
    @staticmethod
    def raise401(detail: str, headers: dict = {"www-Authenticate": "Bearer"}):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )

    @staticmethod
    def raise404(detail: str, headers: dict = {"www-Authenticate": "Bearer"}):
        # FIXME: when should I use this?
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )
