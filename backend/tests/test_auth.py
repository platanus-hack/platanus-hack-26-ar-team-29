from uuid import uuid4

import pytest

from app.api.deps import DEV_USER_ID, parse_dev_user_token, user_id_from_authorization
from app.common.errors import APIError


def test_user_id_from_authorization_accepts_dev_bearer_token() -> None:
    assert user_id_from_authorization(f"Bearer dev-{DEV_USER_ID}") == DEV_USER_ID


def test_parse_dev_user_token_accepts_uuid_payload() -> None:
    user_id = uuid4()

    assert parse_dev_user_token(f"dev-{user_id}") == user_id


@pytest.mark.parametrize("authorization", [None, "", "dev-00000000-0000-0000-0000-000000000001"])
def test_user_id_from_authorization_rejects_missing_bearer(authorization: str | None) -> None:
    with pytest.raises(APIError) as exc_info:
        user_id_from_authorization(authorization)

    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.parametrize("token", [None, "", "invalid", "dev-not-a-uuid"])
def test_parse_dev_user_token_rejects_invalid_token(token: str | None) -> None:
    with pytest.raises(APIError) as exc_info:
        parse_dev_user_token(token)

    assert exc_info.value.code == "UNAUTHORIZED"
