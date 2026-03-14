"""Basic usage example for the ModuleX Python SDK."""

import asyncio

from modulex import Modulex


async def main() -> None:
    async with Modulex(
        api_key="mx_live_your_api_key_here",
        organization_id="your-org-id",
    ) as client:
        # Get current user profile
        me = await client.auth.me()
        print(f"Logged in as: {me['email']}")

        # List organizations
        orgs = await client.auth.organizations()
        for org in orgs["organizations"]:
            print(f"  Org: {org['name']} (role: {org['role']})")

        # List active workflows
        workflows = await client.workflows.list(status="active", page=1, page_size=10)
        print(f"\nActive workflows: {workflows['total']}")
        for wf in workflows["workflows"]:
            print(f"  - {wf['name']} (v{wf.get('version', '?')})")

        # Auto-paginate through all workflows
        print("\nAll workflows:")
        async for wf in client.workflows.list_all(status="active"):
            print(f"  - {wf['name']}")


if __name__ == "__main__":
    asyncio.run(main())
