import asyncio
import json
import logging
import os
import time
from datetime import datetime
from uuid import uuid4

from temporalio.client import Client

from workflows import PreSarfaesiWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded sample loan data
SAMPLE_LOAN_DATA = {
    "loan_uuid": "1818132e-8ec7-4d45-9238-aeef924f9084",
    "loan_no": "L28U3248",
    "portfolio": "Home Loan",
    "borrower_name": "Priyansh Chanda",
    "borrower_contact": "9071909593",
    "state": "Arunachal Pradesh",
    "branch": "Tadipatri",
    "region": "West",
    "sanction_amt": 2681712,
    "current_dpd": 100,
    "date_of_default": "2025-01-26",
    "current_state": "Defaulted",
    "loan_status": "",
    "company_id": "b6d789a6-788f-44a9-9f04-6af3b79f253c",
    "uploaded_date": "2025-03-17T13:06:35.270263+05:30",
    "uploaded_by": "e46f9da6-b924-4168-82dc-6326982642b7",
    "field_group": {}

}
processed_loans = set()


async def check_and_start_workflows():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    logger.info("Connected to Temporal server")
    logger.info("Scheduler started - checking for eligible loans every 2 minutes")
    
    while True:
        try:
            # Get the loan ID
            loan_id = SAMPLE_LOAN_DATA.get('loan_uuid')
            
            # Check if loan DPD matches criteria and hasn't been processed yet
            if (SAMPLE_LOAN_DATA.get('current_dpd', 0) >= 75 and 
                loan_id not in processed_loans):
                
                logger.info(f"=== ELIGIBLE LOAN FOUND: {SAMPLE_LOAN_DATA['loan_no']} with DPD {SAMPLE_LOAN_DATA['current_dpd']} ===")
                
                print(f"\n{'='*80}")
                print(f"STARTING NEW WORKFLOW FOR LOAN: {SAMPLE_LOAN_DATA['loan_no']}")
                print(f"Loan ID: {loan_id}")
                print(f"DPD: {SAMPLE_LOAN_DATA['current_dpd']} days")
                print(f"Borrower: {SAMPLE_LOAN_DATA.get('borrower_name', 'Unknown')}")
                print(f"{'='*80}\n")
                
                # Start the Pre-SARFAESI workflow
                workflow_id = f"pre-sarfaesi-{loan_id}-{uuid4()}"
                
                print(f"Starting workflow with ID: {workflow_id}")
                
                await client.start_workflow(
                    PreSarfaesiWorkflow.run,
                    SAMPLE_LOAN_DATA,
                    id=workflow_id,
                    task_queue="pre-sarfaesi-taskqueue",
                )
                
                processed_loans.add(loan_id)
                
                logger.info(f"Workflow started with ID: {workflow_id}")
            else:
                if loan_id in processed_loans:
                    logger.info(f"Loan {SAMPLE_LOAN_DATA['loan_no']} already has a workflow running.")
                else:
                    logger.info(f"Loan {SAMPLE_LOAN_DATA['loan_no']} not eligible for workflow. DPD: {SAMPLE_LOAN_DATA.get('current_dpd', 0)}")
        
        except Exception as e:
            logger.error(f"Error checking loan eligibility: {e}")
        
        print(f"\nWaiting for 2 minutes before checking again... (Ctrl+C to exit)")
        print(f"Next check at: {datetime.now().replace(microsecond=0).isoformat().replace('T', ' ')} + 2 minutes\n")
        
        await asyncio.sleep(120)


if __name__ == "__main__":
    try:
        asyncio.run(check_and_start_workflows())
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")