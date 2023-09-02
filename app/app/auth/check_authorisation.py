import http

import requests
from jwt_bearer import CheckToken

from app.core.config import settings


def check_authorisation(token: str) -> CheckToken:
    header = {"Authorization": token}
    try:
        response: requests.Response = requests.get(
            url=settings.authentication_url, headers=header
        )
        if response.status_code != http.HTTPStatus.OK:
            return CheckToken(
                is_valid=False, message=f"Request error: {response.status_code}"
            )
        check_token = CheckToken.parse_raw(response.text)
        return check_token
    except requests.exceptions.RequestException as error:
        return CheckToken(is_valid=False, message=error)
