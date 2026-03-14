"""Run a workflow and listen to SSE events."""

import asyncio

from modulex import Modulex


async def main() -> None:
    async with Modulex(
        api_key="mx_live_your_api_key_here",
        organization_id="your-org-id",
    ) as client:
        # Run a saved workflow
        result = await client.executions.run(
            workflow_id="your-workflow-id",
            input={"messages": [{"role": "user", "content": "Hello, world!"}]},
            stream=True,
        )
        print(f"Run started: {result['run_id']}")

        # Listen to execution events via SSE
        async for event in client.executions.listen(result["run_id"]):
            if event.event == "metadata":
                print(f"Workflow: {event.data.get('workflow_name')}")
            elif event.event == "node_update":
                status = event.data.get("status")
                node_id = event.data.get("node_id")
                print(f"  Node '{node_id}': {status}")
                if status == "completed" and "output" in event.data:
                    print(f"    Output: {event.data['output']}")
            elif event.event == "interrupt":
                print(f"  Interrupt: {event.data.get('message')}")
                # Resume with user input
                await client.executions.resume(
                    thread_id=result["thread_id"],
                    run_id=result["run_id"],
                    resume_value="user response here",
                )
            elif event.event == "done":
                print(f"\nCompleted in {event.data.get('total_execution_time_ms')}ms")
                print(f"Steps executed: {event.data.get('steps_executed')}")
            elif event.event == "error":
                print(f"\nError: {event.data.get('error_message')}")


if __name__ == "__main__":
    asyncio.run(main())
