from datetime import datetime

from temporalio import activity


@activity.defn
async def escalate_to_l1(loan_data):
    print(f"Escalating approval request to L1 for loan: {loan_data['loan_no']}")
    
    # Update loan data with escalation information
    loan_data["escalation_status"] = "ESCALATED_TO_L1"
    loan_data["escalation_date"] = datetime.now().isoformat()
    print(f"Escalation notification sent for notice ID: {loan_data['notice_id']}")
    
    return loan_data