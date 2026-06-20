"""Subscription and billing-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class PlanPrice(ModulexModel):
    """A price entry for a plan in GET /subscriptions/organization-plans (uses ``amount``)."""

    interval: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


class DiscountedAmount(ModulexModel):
    """Per-interval discounted prices for a plan (coupon-derived)."""

    month: Optional[float] = None
    year: Optional[float] = None


class OrganizationPlanItem(ModulexModel):
    """A plan in the catalog from GET /subscriptions/organization-plans."""

    plan_slug: Optional[str] = None
    name: Optional[str] = None
    sort_order: int = 0
    is_enterprise: bool = False
    selectable: bool = False
    prices: list[PlanPrice] = Field(default_factory=list)
    discounted_amount: Optional[DiscountedAmount] = None
    badge: Optional[str] = None
    features: list[str] = Field(default_factory=list)
    relation: Optional[str] = None


class OrganizationPlansResponse(ModulexModel):
    """Response from GET /subscriptions/organization-plans."""

    plans: list[OrganizationPlanItem] = Field(default_factory=list)
    total: int = 0


class BillingPlanPrice(ModulexModel):
    """A price entry inside the billing plan object (uses ``price``)."""

    interval: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None


class BillingPlanInfo(ModulexModel):
    """The ``plan`` object in GET /subscriptions/organization-billing."""

    id: str
    name: Optional[str] = None
    plan_slug: Optional[str] = None
    sort_order: int = 0
    is_enterprise: bool = False
    prices: list[BillingPlanPrice] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)


class ScheduledChange(ModulexModel):
    """A pending period-end plan/interval change on a subscription."""

    plan_slug: Optional[str] = None
    interval: Optional[str] = None
    effective_at: Optional[str] = None


class ScheduledCancel(ModulexModel):
    """A pending period-end cancellation on a subscription."""

    cancel_at_period_end: bool = False
    effective_at: Optional[str] = None


class BillingSubscription(ModulexModel):
    """The active subscription object in GET /subscriptions/organization-billing."""

    id: str
    status: Optional[str] = None
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    billing_interval: Optional[str] = None
    current_price: Optional[float] = None
    quantity: int = 1
    scheduled_change: Optional[ScheduledChange] = None
    cancel_at_period_end: bool = False
    scheduled_cancel: Optional[ScheduledCancel] = None
    created_at: Optional[str] = None


class BillingResponse(ModulexModel):
    """Response from GET /subscriptions/organization-billing."""

    has_subscription: bool = False
    subscription: Optional[BillingSubscription] = None
    plan: Optional[BillingPlanInfo] = None


class CheckoutResponse(ModulexModel):
    """Response containing a Stripe checkout or portal URL.

    Covers both POST /subscriptions/checkout-link and POST /subscriptions/customer-portal.
    """

    url: Optional[str] = None
