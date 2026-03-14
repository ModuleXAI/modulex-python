"""Detailed SSE streaming example with all event types."""

import asyncio

from modulex import Modulex


async def handle_workflow_events(client: Modulex, run_id: str) -> None:
    """Handle all SSE event types from workflow execution."""
    async for event in client.executions.listen(run_id):
        if event.event == "metadata":
            print(f"[META] Workflow: {event.data.get('workflow_name')} v{event.data.get('workflow_version')}")
            nodes = event.data.get("nodes", [])
            print(f"  Nodes: {len(nodes)}")

        elif event.event == "node_update":
            node_id = event.data.get("node_id")
            node_type = event.data.get("node_type")
            status = event.data.get("status")
            time_ms = event.data.get("execution_time_ms")

            if status == "started":
                print(f"  [{node_type}] {node_id} started...")
            elif status == "completed":
                print(f"  [{node_type}] {node_id} completed ({time_ms}ms)")
            elif status == "error":
                print(f"  [{node_type}] {node_id} FAILED: {event.data.get('error')}")

        elif event.event == "interrupt":
            print(f"\n[INTERRUPT] {event.data.get('message')}")
            print(f"  Node: {event.data.get('node_id')}")
            print(f"  Instructions: {event.data.get('resume_instructions')}")

        elif event.event == "resumed":
            print(f"[RESUMED] Thread: {event.data.get('thread_id')}")

        elif event.event == "done":
            print(f"\n[DONE] Steps: {event.data.get('steps_executed')}")
            print(f"  Total time: {event.data.get('total_execution_time_ms')}ms")

        elif event.event == "error":
            print(f"\n[ERROR] {event.data.get('error_type')}: {event.data.get('error_message')}")
            if event.data.get("node_id"):
                print(f"  At node: {event.data['node_id']}")

        else:
            print(f"[{event.event}] {event.data}")


async def handle_chat_stream(client: Modulex) -> None:
    """Listen for real-time chat list updates."""
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
        # Run a workflow
        result = await client.executions.run(
            workflow_id="your-workflow-id",
            input={"messages": [{"role": "user", "content": "Analyze this data"}]},
        )

        # Handle all events
        await handle_workflow_events(client, result["run_id"])


if __name__ == "__main__":
    asyncio.run(main())
