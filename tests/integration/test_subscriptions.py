"""Integration tests for the Subscriptions resource.

Covers: organization_plans, organization_billing, checkout_link (skipped),
customer_portal (skipped).
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestSubscriptions:
    """Live API tests for subscription and billing endpoints."""

    async def test_organization_plans(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /subscriptions/organization-plans — response must contain a 'plans' key."""
        async with api_call(tracker, "GET", "/subscriptions/organization-plans") as call:
            result = await client.subscriptions.organization_plans()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "plans" in result, "'plans' key missing from organization plans response"

    async def test_organization_billing(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /subscriptions/organization-billing — response must contain a 'has_subscription' key."""
        async with api_call(tracker, "GET", "/subscriptions/organization-billing") as call:
            result = await client.subscriptions.organization_billing()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "has_subscription" in result, "'has_subscription' key missing from organization billing response"

    async def test_checkout_link(self, tracker: ResultTracker) -> None:
        """POST /subscriptions/checkout-link — skip; creates a Stripe session."""
        skip_call(
            tracker,
            "POST",
            "/subscriptions/checkout-link",
            reason="Creates Stripe session — skipped to avoid side effects",
        )

    async def test_customer_portal(self, tracker: ResultTracker) -> None:
        """POST /subscriptions/customer-portal — skip; creates a Stripe portal session."""
        skip_call(
            tracker,
            "POST",
            "/subscriptions/customer-portal",
            reason="Creates Stripe portal session — skipped to avoid side effects",
        )
