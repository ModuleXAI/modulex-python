"""Subscriptions resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex.types.subscriptions import (
    BillingResponse,
    CheckoutResponse,
    OrganizationPlansResponse,
)


class Subscriptions(_BaseResource):
    """Resource for managing organization subscription plans and billing."""

    async def organization_plans(self, *, organization_id: str | None = None) -> OrganizationPlansResponse:
        """Return available subscription plans for the organization."""
        return OrganizationPlansResponse.model_validate(
            await self._get("/subscriptions/organization-plans", organization_id=organization_id)
        )

    async def organization_billing(self, *, organization_id: str | None = None) -> BillingResponse:
        """Return the current billing details for the organization."""
        return BillingResponse.model_validate(
            await self._get("/subscriptions/organization-billing", organization_id=organization_id)
        )

    async def checkout_link(
        self,
        plan_slug: str,
        interval: str,
        *,
        plan_id: str | None = None,
        organization_id: str | None = None,
    ) -> CheckoutResponse:
        """Generate a Stripe checkout link for upgrading to a given plan and billing interval.

        ``plan_slug`` (e.g. ``"pro"``/``"max"``) is preferred; ``plan_id`` is a legacy/deprecated
        DB plan id. The backend reads these as query parameters.
        """
        params: dict[str, Any] = {"plan_slug": plan_slug, "plan_id": plan_id, "interval": interval}
        return CheckoutResponse.model_validate(
            await self._post(
                "/subscriptions/checkout-link",
                params=params,
                organization_id=organization_id,
            )
        )

    async def customer_portal(self, *, organization_id: str | None = None) -> CheckoutResponse:
        """Generate a Stripe customer portal link for managing the organization's subscription."""
        return CheckoutResponse.model_validate(
            await self._post("/subscriptions/customer-portal", organization_id=organization_id)
        )
