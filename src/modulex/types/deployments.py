"""Deployments-related response models (Pydantic v2).

Field shapes follow the backend deploy routes in ``workflows.py`` (the source of
truth), not the ``modulex-ui`` types which drift. Notable nuances captured here:

- List items (:class:`DeploymentListItem`) are NARROWER than deploy/get records:
  they do NOT include ``workflow_id`` or ``description``.
- ``Deployment`` (deploy response) adds ``workflow_id`` but not the snapshot
  fields (``workflow_schema``/``input``/``config``).
- ``DeploymentDetail`` (get response) is the WIDEST record, adding the immutable
  snapshot fields.
- ``previous_live_deployment_id`` / ``new_live_deployment_id`` are optional: the
  backend omits them in no-op / idempotent cases.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class DeploymentListItem(ModulexModel):
    """A single deployment record from GET /workflows/{id}/deployments (narrow).

    Does NOT include ``workflow_id`` or ``description`` — list items are a
    narrower shape than deploy/get records.
    """

    id: str
    name: Optional[str] = None
    version: Optional[str] = None
    deployment_note: Optional[str] = None
    schema_image_url: Optional[str] = None
    deployed_by: Optional[str] = None
    created_at: Optional[str] = None
    is_live: bool = False


class Deployment(ModulexModel):
    """Deploy response from POST /workflows/{id}/deploy.

    Like a list item plus ``workflow_id``. ``is_live`` is always True at deploy
    time (auto-live), but kept as a bool. Does NOT include the snapshot fields
    (``workflow_schema``/``input``/``config``).
    """

    id: str
    workflow_id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    deployment_note: Optional[str] = None
    schema_image_url: Optional[str] = None
    deployed_by: Optional[str] = None
    created_at: Optional[str] = None
    is_live: bool = False


class DeploymentDetail(Deployment):
    """Get response from GET /workflows/{id}/deployments/{deployment_id} (widest).

    Adds ``description`` and the immutable snapshot fields only present on get.
    """

    description: Optional[str] = None
    workflow_schema: dict[str, Any] = Field(default_factory=dict)
    input: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)


class DeploymentListResponse(ModulexModel):
    """Response from GET /workflows/{id}/deployments."""

    deployments: list[DeploymentListItem] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class DeployRequest(ModulexModel):
    """Request body for POST /workflows/{id}/deploy (all optional)."""

    deployment_note: Optional[str] = None
    schema_image_url: Optional[str] = None


class ActivateDeploymentResponse(ModulexModel):
    """Response from PUT /workflows/{id}/deployments/{deployment_id}/activate.

    ``previous_live_deployment_id`` is omitted when the deployment was already
    live (idempotent case).
    """

    success: bool = True
    message: Optional[str] = None
    deployment_id: Optional[str] = None
    previous_live_deployment_id: Optional[str] = None


class DeactivateDeploymentResponse(ModulexModel):
    """Response from DELETE /workflows/{id}/deployments/live.

    ``previous_live_deployment_id`` is omitted in the no-op case (nothing was
    live). The UI types it as required, which is incorrect.
    """

    success: bool = True
    message: Optional[str] = None
    previous_live_deployment_id: Optional[str] = None


class DeleteDeploymentResponse(ModulexModel):
    """Response from DELETE /workflows/{id}/deployments/{deployment_id}.

    When a live deployment is deleted, the backend auto-rolls back to the
    previous deployment; ``new_live_deployment_id`` carries the new live id (or
    None if none remain).
    """

    success: bool = True
    message: Optional[str] = None
    deleted_deployment_id: Optional[str] = None
    was_live: bool = False
    new_live_deployment_id: Optional[str] = None
