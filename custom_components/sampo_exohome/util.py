"""Define Sampo Smart Home utilities."""

from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.instance_id import async_get
from homeassistant.helpers.storage import Store
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN

from .core.client import async_get_client_with_credentials as cwc
from .core.client import async_get_client_with_token as cwt
from .core.client import Client
from .const import DOMAIN, CONF_USER_ID, CONF_TOKEN_EXPIRES_AT

async def async_get_client_with_credentials(
    hass: HomeAssistant, email: str, password: str
) -> Client:
    """Get a Sampo Smart Home client with credentials."""
    session = aiohttp_client.async_get_clientsession(hass)
    instance_id = await async_get(hass)
    info = await async_load_token(hass, email)
    if info.get(CONF_TOKEN):
        expires_at = int(info.get(CONF_TOKEN_EXPIRES_AT, 0))
        if expires_at - int(datetime.now().timestamp()) > 0:
            return await cwt(email, password, info[CONF_TOKEN], expires_at, session=session, session_name=instance_id)
    client = await cwc(email, password, session=session, session_name=instance_id)
    _, _, expires_at = client.get_login_info()
    info = {
        CONF_PASSWORD: password,
        CONF_TOKEN: client.token,
        CONF_USER_ID: client.id,
        CONF_TOKEN_EXPIRES_AT: expires_at
    }
    await async_store_token(hass, email, info)
    return client


async def async_load_token(
        hass: HomeAssistant, email:str ) -> dict:
    """
    Update tokens in .storage
    """
    default = {
            CONF_PASSWORD: "",
            CONF_TOKEN: "",
            CONF_USER_ID: ""
        }
    store = Store(hass, 1, f"{DOMAIN}/tokens.json")
    data = await store.async_load() or None
    if not data:
        return default
    return data.get(email, default)

async def async_store_token(hass, email: str, info: dict):
    """
    Update tokens in .storage
    """
    store = Store(hass, 1, f"{DOMAIN}/tokens.json")
    data = await store.async_load() or {}
    data = {
        email: info
    }

    await store.async_save(data)