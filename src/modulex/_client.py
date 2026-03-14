"""Main ModuleX client class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from modulex._config import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ClientConfig

if TYPE_CHECKING:
    from modulex.resources.api_keys import ApiKeys
    from modulex.resources.auth import Auth
    from modulex.resources.chats import Chats
    from modulex.resources.composer import Composer
    from modulex.resources.credentials import Credentials
    from modulex.resources.dashboard import Dashboard
    from modulex.resources.deployments import Deployments
    from modulex.resources.executions import Executions
    from modulex.resources.integrations import Integrations
    from modulex.resources.knowledge import Knowledge
    from modulex.resources.notifications import Notifications
    from modulex.resources.organizations import Organizations
    from modulex.resources.schedules import Schedules
    from modulex.resources.subscriptions import Subscriptions
    from modulex.resources.system import System
    from modulex.resources.templates import Templates
    from modulex.resources.workflows import Workflows


class Modulex:
    """Async client for the ModuleX API.

    Usage:
        async with Modulex(api_key="mx_live_...") as client:
            me = await client.auth.me()
    """

    def __init__(
        self,
        api_key: str,
        *,
        organization_id: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._config = ClientConfig(
            api_key=api_key,
            organization_id=organization_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._http = httpx.AsyncClient()

        # Lazy resource cache
        self._auth: object | None = None
        self._workflows: object | None = None
        self._executions: object | None = None
        self._deployments: object | None = None
        self._chats: object | None = None
        self._credentials: object | None = None
        self._integrations: object | None = None
        self._knowledge: object | None = None
        self._schedules: object | None = None
        self._templates: object | None = None
        self._composer: object | None = None
        self._dashboard: object | None = None
        self._subscriptions: object | None = None
        self._notifications: object | None = None
        self._api_keys: object | None = None
        self._system: object | None = None
        self._organizations: object | None = None

    async def __aenter__(self) -> Modulex:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    @property
    def auth(self) -> Auth:
        """Access auth endpoints."""
        if self._auth is None:
            from modulex.resources.auth import Auth

            self._auth = Auth(self)
        return self._auth  # type: ignore[return-value]

    @property
    def workflows(self) -> Workflows:
        """Access workflow endpoints."""
        if self._workflows is None:
            from modulex.resources.workflows import Workflows

            self._workflows = Workflows(self)
        return self._workflows  # type: ignore[return-value]

    @property
    def executions(self) -> Executions:
        """Access execution endpoints."""
        if self._executions is None:
            from modulex.resources.executions import Executions

            self._executions = Executions(self)
        return self._executions  # type: ignore[return-value]

    @property
    def deployments(self) -> Deployments:
        """Access deployment endpoints."""
        if self._deployments is None:
            from modulex.resources.deployments import Deployments

            self._deployments = Deployments(self)
        return self._deployments  # type: ignore[return-value]

    @property
    def chats(self) -> Chats:
        """Access chat endpoints."""
        if self._chats is None:
            from modulex.resources.chats import Chats

            self._chats = Chats(self)
        return self._chats  # type: ignore[return-value]

    @property
    def credentials(self) -> Credentials:
        """Access credential endpoints."""
        if self._credentials is None:
            from modulex.resources.credentials import Credentials

            self._credentials = Credentials(self)
        return self._credentials  # type: ignore[return-value]

    @property
    def integrations(self) -> Integrations:
        """Access integration endpoints."""
        if self._integrations is None:
            from modulex.resources.integrations import Integrations

            self._integrations = Integrations(self)
        return self._integrations  # type: ignore[return-value]

    @property
    def knowledge(self) -> Knowledge:
        """Access knowledge base endpoints."""
        if self._knowledge is None:
            from modulex.resources.knowledge import Knowledge

            self._knowledge = Knowledge(self)
        return self._knowledge  # type: ignore[return-value]

    @property
    def schedules(self) -> Schedules:
        """Access schedule endpoints."""
        if self._schedules is None:
            from modulex.resources.schedules import Schedules

            self._schedules = Schedules(self)
        return self._schedules  # type: ignore[return-value]

    @property
    def templates(self) -> Templates:
        """Access template endpoints."""
        if self._templates is None:
            from modulex.resources.templates import Templates

            self._templates = Templates(self)
        return self._templates  # type: ignore[return-value]

    @property
    def composer(self) -> Composer:
        """Access composer endpoints."""
        if self._composer is None:
            from modulex.resources.composer import Composer

            self._composer = Composer(self)
        return self._composer  # type: ignore[return-value]

    @property
    def dashboard(self) -> Dashboard:
        """Access dashboard endpoints."""
        if self._dashboard is None:
            from modulex.resources.dashboard import Dashboard

            self._dashboard = Dashboard(self)
        return self._dashboard  # type: ignore[return-value]

    @property
    def subscriptions(self) -> Subscriptions:
        """Access subscription endpoints."""
        if self._subscriptions is None:
            from modulex.resources.subscriptions import Subscriptions

            self._subscriptions = Subscriptions(self)
        return self._subscriptions  # type: ignore[return-value]

    @property
    def notifications(self) -> Notifications:
        """Access notification endpoints."""
        if self._notifications is None:
            from modulex.resources.notifications import Notifications

            self._notifications = Notifications(self)
        return self._notifications  # type: ignore[return-value]

    @property
    def api_keys(self) -> ApiKeys:
        """Access API key endpoints."""
        if self._api_keys is None:
            from modulex.resources.api_keys import ApiKeys

            self._api_keys = ApiKeys(self)
        return self._api_keys  # type: ignore[return-value]

    @property
    def system(self) -> System:
        """Access system endpoints."""
        if self._system is None:
            from modulex.resources.system import System

            self._system = System(self)
        return self._system  # type: ignore[return-value]

    @property
    def organizations(self) -> Organizations:
        """Access organization endpoints."""
        if self._organizations is None:
            from modulex.resources.organizations import Organizations

            self._organizations = Organizations(self)
        return self._organizations  # type: ignore[return-value]
