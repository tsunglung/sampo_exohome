"""Define a base client for interacting with Sampo Exohome."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, TypeVar, cast
from uuid import uuid4
import json
import websockets

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientResponseError
from mashumaro import DataClassDictMixin
from mashumaro.exceptions import (
    MissingField,
    SuitableVariantNotFoundError,
    UnserializableDataError,
)

from .errors import InvalidCredentialsError, RequestError
from .model import AuthenticateViaCredentialsResponse
from .const import LOGGER

API_BASE = "https://sampo.apps.exosite.io/api:1"
WSS_BASE = "wss://sampo.apps.exosite.io/api:1"

DEFAULT_TIMEOUT = 10

ExohomeBaseModelT = TypeVar("ExohomeBaseModelT", bound=DataClassDictMixin)

class Client:
    """Define the API object."""

    def __init__(
        self, *, session: ClientSession | None = None, session_name: str | None = None
    ) -> None:
        """Initialize.

        Args:
        ----
            session: An optional aiohttp ClientSession.
            session_name: An optional session name to use for authentication.

        """
        self._provision_token: str | None = None
        self._provision_token_expires_in: datetime | None = None
        self._session = session
        self._session_name = session_name or uuid4().hex
        self._default_context = None
        self._email: str = ""
        self._password: str = ""
        self._expires_at = 0
        self.id: str = ""
        self.token: str = ""
        self.ws = None
        self.devices: dict = {}
        self._ws_id = 0

    async def async_set_token(
        self, email: str, password: str, token: str, expires_at: int
    ) -> None:
        """Authenticate via username and password.

        Args:
        ----
            email: The email address of a Sampo Smart Home account.
            password: The account password.

        """
        self._email = email
        self._password = password
        self._expires_at = expires_at
        self.token = token

    async def async_authenticate_from_credentials(
        self, email: str, password: str
    ) -> None:
        """Authenticate via username and password.

        Args:
        ----
            email: The email address of a Sampo Smart Home account.
            password: The account password.

        """
        auth_response: AuthenticateViaCredentialsResponse = (
            await self.async_request_and_validate(
                "post",
                "/session",
                AuthenticateViaCredentialsResponse,
                headers={},
                json_data={
                    "email": email,
                    "password": password,
                },
            )
        )

        self.id = auth_response.id
        self.token = auth_response.token
        self._expires_at = int(
            datetime.now().timestamp() + timedelta(days=29).total_seconds()
        )

    async def async_request(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request.

        Args:
        ----
            method: An HTTP method.
            endpoint: A relative API endpoint.
            headers: Additional headers to include in the request.
            json: A JSON payload to send with the request.

        Returns:
        -------
            An API response payload.

        Raises:
        ------
            InvalidCredentialsError: Raised upon invalid credentials.
            RequestError: Raised upon an underlying HTTP error.

        """
        url: str = f"{API_BASE}{endpoint}"

        headers = {}
        session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        data: dict[str, Any] = {}

        async with session.request(method, url, headers=headers, json=json_data) as resp:
            try:
                data = await resp.json()
            except Exception as e:
                LOGGER.error(f"json {resp} {e}")

            try:
                resp.raise_for_status()
            except ClientResponseError as err:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    msg = "Invalid credentials"
                    raise InvalidCredentialsError(msg) from err
                raise RequestError(data["errors"][0]["title"]) from err

        await session.close()

        LOGGER.debug("Received data from %s: %s", endpoint, data)

        return data

    async def async_request_and_validate(
        self,
        method: str,
        endpoint: str,
        model: type[DataClassDictMixin],
        *,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> ExohomeBaseModelT:
        """Make an API request and validate the response.

        Args:
        ----
            method: An HTTP method.
            endpoint: A relative API endpoint.
            headers: Additional headers to include in the request.
            json: A JSON payload to send with the request.

        Returns:
        -------
            A parsed, validated Pydantic model representing the response.

        """
        raw_data = await self.async_request(
            method,
            endpoint,
            headers=headers,
            json_data=json_data,
        )

        try:
            return cast(ExohomeBaseModelT, model.from_dict(raw_data))
        except (
            MissingField,
            SuitableVariantNotFoundError,
            UnserializableDataError,
        ) as err:
            msg = f"Error while parsing response from {endpoint}: {err}"
            raise RequestError(msg) from err

    async def get_fw_list(self):
        """Get firmware update list.

        Returns:
            update list.

        Raises:
            NoAuthError: If the ID token is not available.
            ValueError: If the ClientSession or Endpoints are not available.
            ApiError: If an API error occurs.
        """
        if len(self.devices) <= 1:
            return []

        models = []
        for _, info in self.devices.items():
            models.appen(info["properties"]["profile"]["esh"]["model"])
        headers = {}
        json_data = {}
        endpoint = f"/fw/list/{str(models)}"
        raw_data = await self.async_request(
            "GET",
            endpoint,
            headers=headers,
            json_data=json_data,
        )
        try:
            return json.loads(raw_data)
        except:
            return []

    def _format_msg(self, id, request, device=None, data=None):
        datas = {}
        datas["id"] = id
        datas["request"] = request
        if device:
            datas["device"] = device
        if data:
            datas["data"] = data
        return datas

    async def _ws_write(self, msg: dict) -> dict:
        id = msg["id"]
        request = msg["request"]
        for i in range(0, 2):
            await self.ws.send(json.dumps(msg))
            #if msg.get("device"):
            #    await asyncio.sleep(.1)
            try:
                text = await self.ws.recv()
                response = json.loads(text)
            except websockets.exceptions.ConnectionClosed as err:
                msg = f"Error while parsing response from {msg}: {err}"
            except Exception as err:
                msg = f"Error while parsing response from {msg}: {err}"
                raise RequestError(msg) from err
            if response.get("status"):
                if request == response.get("response"):
                    return response
        return {}

    async def ws_connect(self, default_context):
        """websocket connect.

        Returns:
            websocket handle

        Raises:
            NoAuthError: If the ID token is not available.
            ValueError: If the ClientSession or Endpoints are not available.
            ApiError: If an API error occurs.
        """
        self._default_context = default_context
        async with websockets.connect(f"{WSS_BASE}/phone", ssl=self._default_context, close_timeout=3) as websocket:
            self.ws = websocket
            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "login", data={"token": self.token})
            response = await self._ws_write(msg)

            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "provision_token", data={"expires_in": 2592000})
            response = await self._ws_write(msg)
            if isinstance(response, dict) and response["status"] == "ok":
                self._provision_token = response["data"]["token"]
                self._provision_token_expires_in = response["data"]["expires_in"]

            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "get_user_data")
            response = await self._ws_write(msg)

            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "get_me")
            response = await self._ws_write(msg)

        LOGGER.debug(f"token: {self._provision_token}, expires_in: {self._provision_token_expires_in}")

    async def ws_close(self):
        """websocket close.

        Returns:

        Raises:

        """
        if self.ws:
            await self.ws.close()

    async def get_all_devices(self):
        """Get all devices.

        Returns:
            A list of all device.

        Raises:
            NoAuthError: If the ID token is not available.
            ValueError: If the ClientSession or Endpoints are not available.
            ApiError: If an API error occurs.
        """
        devices = []
        new_devices = {}
        if self._expires_at - int(datetime.now().timestamp()) <= 0:
            self.async_authenticate_from_credentials(self._email, self._password)

        async with websockets.connect(f"{WSS_BASE}/phone", ssl=self._default_context, close_timeout=3) as websocket:
            self.ws = websocket
            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "login", data={"token": self.token})
            response = await self._ws_write(msg)

            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "lst_device")
            response = await self._ws_write(msg)
            if isinstance(response, dict) and response.get("status") == "ok":
                devices = response["data"]

            await self.ws.recv()

            for dev in devices:
                device = dev.get("device", None)
                if device is None:
                    continue
                msg = self._format_msg(self._ws_id, "get", device=device)
                self._ws_id = self._ws_id + 1
                response = await self._ws_write(msg)
                if isinstance(response, dict) and response.get("status") == "ok":
                    data = response["data"]
                    if data["device"] == device:
                        dev["properties"].update(data)
                        new_devices[device] = dev
        if len(new_devices) >= 1:
            for device, info in new_devices.items():
                self.devices[device] = info

        return self.devices

    async def set_device(self, device, func, value):
        """Set device.

        Returns:


        Raises:
            NoAuthError: If the ID token is not available.
            ValueError: If the ClientSession or Endpoints are not available.
            ApiError: If an API error occurs.
        """
        data = {func: value}
        async with websockets.connect(f"{WSS_BASE}/phone", ssl=self._default_context, close_timeout=3) as websocket:
            self.ws = websocket
            self._ws_id = self._ws_id + 1
            msg = self._format_msg(self._ws_id, "login", data={"token": self.token})
            await self._ws_write(msg)

            msg = self._format_msg(self._ws_id, "set", device=device, data=data)
            self._ws_id = self._ws_id + 1
            await self._ws_write(msg)

    def get_login_info(self):
        """ Get info of login

        Returns:
            email, password, expires_at

        """

        return self._email, self._password, self._expires_at

async def async_get_client_with_credentials(
    email: str,
    password: str,
    *,
    session: ClientSession | None = None,
    session_name: str | None = None,
) -> Client:
    """Return an authenticated API object (using username/password).

    Args:
    ----
        email: The email address of a Sampo Smart Home account.
        password: The account password.
        session: An optional aiohttp ClientSession.
        session_name: An optional session name to use for authentication.

    Returns:
    -------
        An authenticated Client object.

    """
    client = Client(session=session, session_name=session_name)
    await client.async_authenticate_from_credentials(email, password)
    return client

async def async_get_client_with_token(
    email: str,
    password: str,
    token: str,
    expires_at: int,
    *,
    session: ClientSession | None = None,
    session_name: str | None = None,
) -> Client:
    """Return an authenticated API object (using username/password).

    Args:
    ----
        email: The email address of a Sampo Smart Home account.
        password: The account password.
        session: An optional aiohttp ClientSession.
        session_name: An optional session name to use for authentication.

    Returns:
    -------
        An authenticated Client object.

    """
    client = Client(session=session, session_name=session_name)
    await client.async_set_token(email, password, token, expires_at)
    return client
