"""Subscriptions resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Subscriptions(_BaseResource):
    """Resource for managing organization subscription plans and billing."""

    async def organization_plans(self, *, organization_id: str | None = None) -> Any:
        """Return available subscription plans for the organization."""
        return await self._get("/subscriptions/organization-plans", organization_id=organization_id)

    async def organization_billing(self, *, organization_id: str | None = None) -> Any:
        """Return the current billing details for the organization."""
        return await self._get("/subscriptions/organization-billing", organization_id=organization_id)

    async def checkout_link(
        self,
        plan_id: str,
        interval: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Generate a Stripe checkout link for upgrading to a given plan and billing interval."""
        params: dict[str, Any] = {"plan_id": plan_id, "interval": interval}
        return await self._post(
            "/subscriptions/checkout-link",
            json=params,
            organization_id=organization_id,
        )

    async def customer_portal(self, *, organization_id: str | None = None) -> Any:
        """Generate a Stripe customer portal link for managing the organization's subscription."""
        return await self._post("/subscriptions/customer-portal", organization_id=organization_id)
