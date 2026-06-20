"""Detailed SSE streaming example with all event types.

The backend emits workflow/composer/assistant events as raw ``data: {"type": ...}``
frames (no SSE ``event:`` line). The SDK normalizes this so ``event.event`` carries
the logical type. Note the nesting: ``interrupt`` and ``error`` carry their payload
under ``event.data["data"]``, while ``node_update``/``done`` fields are root-level.
"""

import asyncio

from modulex import Modulex


async def handle_workflow_events(client: Modulex, run_id: str) -> None:
    """Handle all SSE event types from workflow execution."""
    async for event in client.executions.listen(run_id):
        if event.event == "metadata":
            print(f"[META] workflow_type={event.data.get('workflow_type')}")

        elif event.event == "node_update":
            # node_update fields are root-level (no "data" wrapper).
            node_id = event.data.get("node_id")
            node_type = event.data.get("node_type")
            status = event.data.get("status")  # started | completed | error
            time_ms = event.data.get("execution_time_ms")

            if status == "started":
                print(f"  [{node_type}] {node_id} started...")
            elif status == "completed":
                print(f"  [{node_type}] {node_id} completed ({time_ms}ms)")
            elif status == "error":
                print(f"  [{node_type}] {node_id} FAILED: {event.data.get('error')}")

        elif event.event == "interrupt":
            # InterruptEventData is nested under data["data"].
            payload = event.data.get("data", {})
            print(f"\n[INTERRUPT] {payload.get('message')}")
            print(f"  Node: {payload.get('node_id')}")
            print(f"  Instructions: {payload.get('resume_instructions')}")

        elif event.event == "done":
            # Terminal event — the stream stops after this. Fields are root-level.
            print(f"\n[DONE] Steps: {event.data.get('steps_executed')}")
            print(f"  Total time: {event.data.get('total_execution_time_ms')}ms")

        elif event.event == "error":
            # ErrorEventData is nested under data["data"]. Terminal event.
            payload = event.data.get("data", {})
            print(f"\n[ERROR] {payload.get('error_type')}: {payload.get('error_message')}")
            if payload.get("node_id"):
                print(f"  At node: {payload['node_id']}")

        elif event.event == "cancelled":
            # Terminal — fields are root-level.
            print(f"\n[CANCELLED] reason={event.data.get('reason')}")

        else:
            print(f"[{event.event}] {event.data}")


async def handle_chat_stream(client: Modulex) -> None:
    """Listen for real-time chat list updates (A-group: real SSE event: names)."""
    async for event in client.chats.stream():
        if event.event == "connected":
            print("Connected to chat stream")
        elif event.event == "chat_list_updated":
            print(f"Chat list updated: {event.data.get('type')} at {event.data.get('timestamp')}")


async def main() -> None:
    async with Modulex(
        api_key="mx_live_your_api_key_here",
        organization_id="your-org-id",
    ) as client:
        # Run a workflow, then listen to its event stream.
        result = await client.executions.run(
            workflow_id="your-workflow-id",
            input={"messages": [{"role": "user", "content": "Analyze this data"}]},
        )
        await handle_workflow_events(client, result["run_id"])


if __name__ == "__main__":
    asyncio.run(main())
