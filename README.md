# Pre-SARFAESI Temporal Workflow

This project implements a Temporal workflow for managing the Pre-SARFAESI process for loan defaults. The workflow automates the notice generation, approval, escalation, and registered post task creation process.

## Overview

The Pre-SARFAESI workflow consists of the following steps:

1. **Trigger**: When a loan's Days Past Due (DPD) reaches 75 or more
2. **Notice Generation**: System generates a Pre-SARFAESI Notice
3. **Legal Manager Approval**: Legal manager has 2 days to approve the notice
4. **Escalation**: If approval is not received within 2 days, escalate to L1
5. **Post Approval**: Once approved, create a task to send the notice via registered post

## Project Structure

```
pre_sarfaesi_temporal/
│── activities/
│   │── __init__.py
│   │── generate_notice.py
│   │── legal_manager_approval.py
│   │── escalate_to_l1.py
│   │── send_registered_post.py
│── workflows/
│   │── __init__.py
│   │── pre_sarfaesi_workflow.py
│── worker.py
│── scheduler.py
│── manual_approval.py
│── requirements.txt
```

## How to Run

1. **Setup Temporal Server using Docker Compose**:

   Clone the Temporal docker-compose repository:
   ```
   git clone https://github.com/temporalio/docker-compose.git
   cd docker-compose
   ```

   Create a `.env` file in the docker-compose directory with the following content:
   ```
   COMPOSE_PROJECT_NAME=temporal
   CASSANDRA_VERSION=3.11.9
   ELASTICSEARCH_VERSION=7.16.2
   MYSQL_VERSION=8
   TEMPORAL_VERSION=1.25.0
   TEMPORAL_ADMINTOOLS_VERSION=1.25.0-tctl-1.18.1-cli-1.0.0
   TEMPORAL_UI_VERSION=2.26.2
   POSTGRESQL_VERSION=13
   POSTGRES_PASSWORD=temporal
   POSTGRES_USER=temporal
   POSTGRES_DEFAULT_PORT=5432
   OPENSEARCH_VERSION=2.5.0
   ```

   Start the Temporal server with PostgreSQL:
   ```
   sudo docker-compose up
   ```

   This will start the Temporal server with PostgreSQL backend.

2. **Install Python Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Start the Worker**: Run the worker to process workflow tasks
   ```
   python worker.py
   ```

4. **Start the Scheduler**: Run the scheduler to check for eligible loans and start workflows
   ```
   python scheduler.py
   ```

5. **Approve Notices**: Use the approval client to approve generated notices
   ```
   python manual_approval.py
   ```

## Components

### Scheduler

The scheduler checks for loans with DPD ≥ 75 every 2 minutes and starts a workflow for eligible loans.

### Worker

The worker processes the workflow tasks and activities, connecting to the Temporal server.

### Approval Client

A simple client that allows legal managers and L1 approvers to:
1. List pending workflows that need approval
2. Select a workflow by number
3. Send an approval signal to the selected workflow

### Activities

- **generate_notice**: Generates a Pre-SARFAESI Notice for the loan
- **request_legal_manager_approval**: Requests approval from the legal manager
- **escalate_to_l1**: Escalates the approval process to L1 if the deadline is missed
- **send_registered_post**: Creates a task to send the notice via registered post

### Workflow

The main workflow orchestrates the entire process, managing the approval deadline, escalation to L1, and ensuring the proper sequence of activities.

