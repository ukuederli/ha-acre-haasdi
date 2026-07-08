"""Acre SPC42 API Client."""

from __future__ import annotations

import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup


class AcreApiClientError(Exception):
    """Exception to indicate a general API error."""


class AcreApiClientCommunicationError(AcreApiClientError):
    """Exception to indicate a communication error."""


class AcreApiClientAuthenticationError(AcreApiClientError):
    """Exception to indicate an authentication error."""


class AcreApiClient:
    """Acre SPC42 API Client using web scraping."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the Acre API Client."""
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._session = session
        self._session_id: str | None = None

    async def async_login(self) -> None:
        """Login to the Acre panel and store session ID."""
        url = f"http://{self._host}/login.htm"
        params = {"action": "login", "language": "253"}
        data = {
            "userid": self._username,
            "password": self._password,
        }
        try:
            async with self._session.post(
                url,
                params=params,
                data=data,
                allow_redirects=True,
            ) as response:
                if response.status != 200:
                    raise AcreApiClientAuthenticationError(
                        f"Login failed with status {response.status}"
                    )
                final_url = str(response.url)
                match = re.search(r"session=(0x[0-9A-Fa-f]+)", final_url)
                if not match:
                    body = await response.text()
                    match = re.search(r"session=(0x[0-9A-Fa-f]+)", body)
                if not match:
                    raise AcreApiClientAuthenticationError(
                        "Could not extract session ID - check credentials"
                    )
                self._session_id = match.group(1)
        except aiohttp.ClientError as exception:
            raise AcreApiClientCommunicationError(
                f"Error connecting to Acre panel: {exception}"
            ) from exception

    async def async_get_zones(self, retry: bool = True) -> list[dict[str, Any]]:
        """Get zone status from the Acre panel."""
        url = f"http://{self._host}/secure.htm"
        params = {
            "session": self._session_id,
            "page": "status_zones",
        }
        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    raise AcreApiClientCommunicationError(
                        f"Failed to get zones: status {response.status}"
                    )
                body = await response.text()
                if ("login.htm" in body or "action=login" in body) and retry:
                    self._session_id = None
                    await self.async_login()
                    return await self.async_get_zones(retry=False)
                return self._parse_zones(body)
        except aiohttp.ClientError as exception:
            raise AcreApiClientCommunicationError(
                f"Error fetching zones: {exception}"
            ) from exception

    def _parse_zones(self, html: str) -> list[dict[str, Any]]:
        """Parse zone table from HTML response."""
        soup = BeautifulSoup(html, "html.parser")
        zones = []
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                zone_name = cells[0].get_text(strip=True)
                area = cells[1].get_text(strip=True)
                zone_type = cells[2].get_text(strip=True)
                status = cells[3].get_text(strip=True)
                if not zone_name or zone_name in ("Zone", ""):
                    continue
                if not zone_name[0].isdigit():
                    continue
                zones.append(
                    {
                        "id": zone_name.split(" ")[0],
                        "name": zone_name,
                        "area": area,
                        "zone_type": zone_type,
                        "status": status,
                        "is_triggered": status.lower() == "actuated",
                    }
                )
        return zones

    async def async_get_alarm_status(self, retry: bool = True) -> dict[str, Any]:
        """Get alarm arm/disarm status from the Acre panel."""
        url = f"http://{self._host}/secure.htm"
        params = {
            "session": self._session_id,
            "page": "system_summary",
        }
        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    raise AcreApiClientCommunicationError(
                        f"Failed to get alarm status: status {response.status}"
                    )
                body = await response.text()
                if ("login.htm" in body or "action=login" in body) and retry:
                    self._session_id = None
                    await self.async_login()
                    return await self.async_get_alarm_status(retry=False)
                return self._parse_alarm_status(body)
        except aiohttp.ClientError as exception:
            raise AcreApiClientCommunicationError(
                f"Error fetching alarm status: {exception}"
            ) from exception

    def _parse_alarm_status(self, html: str) -> dict[str, Any]:
        """Parse alarm status from system_summary HTML."""
        soup = BeautifulSoup(html, "html.parser")

        status = "unknown"
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            for i, cell in enumerate(cells):
                if "All Areas" in cell.get_text():
                    for next_cell in cells[i + 1 :]:
                        text = next_cell.get_text(strip=True)
                        if text:
                            status = text.lower()
                            break
                    break

        active_mode = "unset"
        inputs = soup.find_all("input", {"type": "submit"})
        for inp in inputs:
            if not inp.get("disabled"):
                name = inp.get("name", "")
                if "partset_a" in name:
                    active_mode = "part_set_a"
                elif "partset_b" in name:
                    active_mode = "part_set_b"
                elif "fullset" in name:
                    active_mode = "fullset"

        return {
            "status": status,
            "active_mode": active_mode,
            "is_armed": status != "unset",
        }

    async def async_get_data(self) -> dict[str, Any]:
        """Get all data from the Acre panel."""
        if not self._session_id:
            await self.async_login()
        zones = await self.async_get_zones()
        alarm_status = await self.async_get_alarm_status()
        return {"zones": zones, "alarm_status": alarm_status}
