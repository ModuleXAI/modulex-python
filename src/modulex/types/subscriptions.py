"""Subscription and billing-related type definitions."""

from __future__ import annotations

from typing_extensions import TypedDict


class PlanPrice(TypedDict, total=False):
    """Pricing entry for a subscription plan."""

    price: float
    interval: str
    currency: str


class PlanInfo(TypedDict, total=False):
    """Details about a subscription plan."""

    id: str
    name: str
    sort_order: int
    is_enterprise: bool
    discount: float | None
    prices: list[PlanPrice]
    features: list[str]
    is_selectable: bool


class PlansResponse(TypedDict, total=False):
    """Response listing available subscription plans."""

    plans: list[PlanInfo]
    total: int


class BillingSubscription(TypedDict, total=False):
    """Active billing subscription details."""

    id: str
    status: str
    current_period_start: str
    current_period_end: str
    billing_interval: str
    current_price: float | None
    created_at: str


class BillingResponse(TypedDict, total=False):
    """Current billing state for an organization."""

    has_subscription: bool
    subscription: BillingSubscription
    plan: PlanInfo


class CheckoutResponse(TypedDict, total=False):
    """Response containing a Stripe checkout or portal URL."""

    url: str
