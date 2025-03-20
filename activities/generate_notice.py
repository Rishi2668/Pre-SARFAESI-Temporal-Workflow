import json
import os
from datetime import datetime

from temporalio import activity


@activity.defn
async def generate_notice(loan_data):
    print(f"Generating Pre-SARFAESI notice for loan: {loan_data['loan_no']}")
    
    # Generate a unique notice ID
    notice_id = f"NOTICE-{loan_data['loan_no']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Update loan data with notice information
    loan_data["notice_id"] = notice_id
    loan_data["notice_date"] = datetime.now().isoformat()
    loan_data["notice_status"] = "GENERATED"
    
    print(f"Notice generated with ID: {notice_id}")
    
    return loan_data