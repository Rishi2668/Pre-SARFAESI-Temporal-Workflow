from datetime import datetime

from temporalio import activity


@activity.defn
async def send_registered_post(loan_data):
    print(f"Creating task to send notice via registered post for loan: {loan_data['loan_no']}")
    
    loan_data["registered_post_status"] = "TASK_CREATED"
    loan_data["registered_post_task_date"] = datetime.now().isoformat()
    
    tracking_id = f"RP-{loan_data['loan_no']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    loan_data["registered_post_tracking_id"] = tracking_id
    
    print(f"Registered post task created with tracking ID: {tracking_id}")
    
    return loan_data