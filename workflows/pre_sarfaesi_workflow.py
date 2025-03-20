import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import (
        generate_notice,
        request_legal_manager_approval,
        escalate_to_l1,
        send_registered_post,
    )


@workflow.defn
class PreSarfaesiWorkflow:
    def __init__(self):
        self.approval_received = False
        self.loan_data = {}
    
    @workflow.signal
    def approve_notice(self):
        self.approval_received = True
        workflow.logger.info(f"Notice approval signal received for loan: {self.loan_data.get('loan_no', 'Unknown')}")

    @workflow.run
    async def run(self, loan_data: dict) -> dict:

        self.loan_data = loan_data
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(minutes=10),
            maximum_attempts=5,
        )
        
        # Step 1: Generate Pre-SARFAESI Notice
        print(f"Generating Pre-SARFAESI Notice for loan: {loan_data.get('loan_no', 'Unknown')}")
        loan_data = await workflow.execute_activity(
            generate_notice,
            loan_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )
        print(f"Notice generated with ID: {loan_data.get('notice_id', 'Unknown')}")
        
        # Step 2: Request Legal Manager Approval
        print(f"Requesting Legal Manager Approval for notice: {loan_data.get('notice_id', 'Unknown')}")
        loan_data = await workflow.execute_activity(
            request_legal_manager_approval,
            loan_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )
        
        # Step 3: Wait for approval signal with a deadline of 2 days
        approval_timeout = timedelta(days=2)
        approval_deadline = workflow.now() + approval_timeout
        
        print(f"Waiting for Legal Manager Approval - Deadline: {approval_deadline}")
        while workflow.now() < approval_deadline and not self.approval_received:
            try:
            
                await asyncio.sleep(30) 
            except asyncio.CancelledError:
          
                break
                
        if self.approval_received:
            print(f"Approval received for notice: {loan_data.get('notice_id', 'Unknown')}")
        
        # Step 4: If approval not received, escalate to L1
        if not self.approval_received:
            print(f"Approval deadline expired - Escalating to L1 for notice: {loan_data.get('notice_id', 'Unknown')}")
            loan_data = await workflow.execute_activity(
                escalate_to_l1,
                loan_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )
            
            print(f"Waiting for L1 Approval after escalation for notice: {loan_data.get('notice_id', 'Unknown')}")
            # Keep waiting for approval signal after escalation
            while not self.approval_received:
                try:
                    await asyncio.sleep(60)  # Check every minute
                except asyncio.CancelledError:
                    
                    break
            
            print(f"L1 Approval received for notice: {loan_data.get('notice_id', 'Unknown')}")
        
        # Step 5: Create task to send notice via registered post after approval
        print(f"Creating task to send notice via registered post for notice: {loan_data.get('notice_id', 'Unknown')}")
        loan_data = await workflow.execute_activity(
            send_registered_post,
            loan_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )
        
        print(f"Workflow completed successfully for loan: {loan_data.get('loan_no', 'Unknown')}")
        return loan_data