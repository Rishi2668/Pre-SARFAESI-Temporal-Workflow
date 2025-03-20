import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import (
    generate_notice,
    request_legal_manager_approval,
    # check_approval_status,
    escalate_to_l1,
    send_registered_post,
)
from workflows import PreSarfaesiWorkflow


async def run_worker():
    """
    Start a Temporal worker to process pre-SARFAESI workflows
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting Pre-SARFAESI worker")

    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    logger.info("Connected to Temporal server")

    # Create a worker for the pre-SARFAESI task queue
    worker = Worker(
        client,
        task_queue="pre-sarfaesi-taskqueue",
        workflows=[PreSarfaesiWorkflow],
        activities=[
            generate_notice,
            request_legal_manager_approval,
            # check_approval_status,
            escalate_to_l1,
            send_registered_post,
        ],
    )

    # Start the worker
    logger.info("Worker starting on task queue: pre-sarfaesi-taskqueue")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())