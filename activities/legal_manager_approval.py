from datetime import datetime

from temporalio import activity


@activity.defn
async def request_legal_manager_approval(loan_data):
    print(f" Requesting legal manager approval for notice ID: {loan_data['notice_id']}")
    
    # This is where you would typically send a notification to the legal manager
    print(f" Approval request sent for loan: {loan_data['loan_no']}")
    
    # Return the loan data without modification
    return loan_data