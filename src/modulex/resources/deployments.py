"""Deployments resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex.types.deployments import (
    ActivateDeploymentResponse,
    DeactivateDeploymentResponse,
    DeleteDeploymentResponse,
    Deployment,
    DeploymentDetail,
    DeploymentListResponse,
)


class Deployments(_BaseResource):
    """Resource for managing workflow deployments."""

    async def create(
        self,
        workflow_id: str,
        *,
        deployment_note: str | None = None,
        schema_image_url: str | None = None,
        organization_id: str | None = None,
    ) -> Deployment:
        """Deploy a workflow and create a new deployment record."""
        body: dict[str, Any] = {}
        if deployment_note is not None:
            body["deployment_note"] = deployment_note
        if schema_image_url is not None:
            body["schema_image_url"] = schema_image_url
        return Deployment.model_validate(
            await self._post(
                f"/workflows/{workflow_id}/deploy",
                json=body or None,
                organization_id=organization_id,
            )
        )

    async def list(
        self,
        workflow_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> DeploymentListResponse:
        """Return a paginated list of deployments for a workflow."""
        return DeploymentListResponse.model_validate(
            await self._get(
                f"/workflows/{workflow_id}/deployments",
                params={"limit": limit, "offset": offset},
                organization_id=organization_id,
            )
        )

    async def get(
        self,
        workflow_id: str,
        deployment_id: str,
        *,
        organization_id: str | None = None,
    ) -> DeploymentDetail:
        """Return a single deployment by workflow ID and deployment ID."""
        return DeploymentDetail.model_validate(
            await self._get(
                f"/workflows/{workflow_id}/deployments/{deployment_id}",
                organization_id=organization_id,
            )
        )

    async def activate(
        self,
        workflow_id: str,
        deployment_id: str,
        *,
        organization_id: str | None = None,
    ) -> ActivateDeploymentResponse:
        """Activate a specific deployment, making it the live version."""
        return ActivateDeploymentResponse.model_validate(
            await self._put(
                f"/workflows/{workflow_id}/deployments/{deployment_id}/activate",
                organization_id=organization_id,
            )
        )

    async def deactivate(self, workflow_id: str, *, organization_id: str | None = None) -> DeactivateDeploymentResponse:
        """Deactivate the currently live deployment for a workflow."""
        return DeactivateDeploymentResponse.model_validate(
            await self._delete(
                f"/workflows/{workflow_id}/deployments/live",
                organization_id=organization_id,
            )
        )

    async def delete(
        self,
        workflow_id: str,
        deployment_id: str,
        *,
        organization_id: str | None = None,
    ) -> DeleteDeploymentResponse:
        """Permanently delete a deployment by workflow ID and deployment ID."""
        return DeleteDeploymentResponse.model_validate(
            await self._delete(
                f"/workflows/{workflow_id}/deployments/{deployment_id}",
                organization_id=organization_id,
            )
        )
