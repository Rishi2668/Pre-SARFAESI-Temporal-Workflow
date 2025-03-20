import asyncio
from temporalio.client import Client

async def list_and_approve_workflows():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Get all running workflows
    workflows = []
    async for workflow_handle in client.list_workflows(
        query="WorkflowType='PreSarfaesiWorkflow' AND ExecutionStatus='Running'"
    ):
        workflows.append({
            "workflow_id": workflow_handle.id,
            "run_id": workflow_handle.run_id,
        })
    
    if not workflows:
        print("No pending workflows found.")
        return
    
    # Display workflows
    print("\nPending workflows:")
    for i, workflow in enumerate(workflows, 1):
        print(f"{i}. {workflow['workflow_id']}")
    
    # Get selection and approve
    try:
        choice = input("\nSelect workflow to approve (number): ")
        idx = int(choice) - 1
        
        if 0 <= idx < len(workflows):
            selected = workflows[idx]['workflow_id']
            handle = client.get_workflow_handle(selected)
            await handle.signal("approve_notice")
            print(f"Workflow approved: {selected}")
        else:
            print("Invalid selection.")
    
    except (ValueError, IndexError):
        print("Invalid input.")

if __name__ == "__main__":
    asyncio.run(list_and_approve_workflows())