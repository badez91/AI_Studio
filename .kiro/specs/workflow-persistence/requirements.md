# Requirements Document

## Introduction

This document establishes the formal requirement baseline for the Workflow Persistence feature of AI Studio. Workflow Persistence enables durable storage of workflow execution state in a SQLite database via SQLAlchemy, supports resuming failed workflows from their last successful step, and provides conflict detection to prevent re-execution of terminal workflows. The feature bridges the in-memory WorkflowEngine with persistent storage through a WorkflowRepository that handles bidirectional conversion between the database model (Job) and the engine model (WorkflowContext).

## Glossary

- **Job**: The SQLAlchemy ORM model representing a persisted workflow execution record in the database. Contains id, name, status, payload, current_step, results_json, errors_json, created_at, and updated_at fields.
- **WorkflowContext**: An in-memory dataclass used by the WorkflowEngine to track execution state, current step, results, and errors during a workflow run.
- **WorkflowRepository**: The data access component that provides create, get, update, and list operations on Job records, and converts between Job and WorkflowContext representations.
- **WorkflowEngine**: The sequential step executor that processes workflow steps and updates a WorkflowContext with results or errors.
- **WorkflowState**: An enumeration of valid workflow lifecycle states: pending, running, completed, failed, and cancelled.
- **Workflow_API**: The FastAPI REST interface that exposes workflow submission, status retrieval, and execution endpoints.
- **Resume**: The act of re-executing a previously failed workflow, skipping steps that already completed successfully.
- **Conflict_Detection**: The mechanism that prevents re-execution of workflows in a terminal state (completed or cancelled).

## Requirements

### Requirement 1: Workflow Creation and Identification

**User Story:** As a platform operator, I want each workflow to be created with a unique identifier and persisted immediately, so that I can track and reference workflow executions reliably.

#### Acceptance Criteria

1. WHEN a new workflow is submitted, THE WorkflowRepository SHALL create a Job record with a UUID v4 identifier stored as a 36-character string.
2. WHEN a new workflow is created, THE WorkflowRepository SHALL set the initial status to "pending", current_step to 0, results_json to "[]", and errors_json to "[]".
3. WHEN a new workflow is created, THE WorkflowRepository SHALL persist the Job record to the SQLite database and return the committed record with a generated id.
4. THE Job model SHALL store the id field as a String(36) primary key column.

### Requirement 2: Workflow State Persistence

**User Story:** As a platform operator, I want workflow execution state to be persisted after each state change, so that the system can recover from crashes and I can observe progress.

#### Acceptance Criteria

1. WHEN the WorkflowRepository update_state method is called, THE WorkflowRepository SHALL persist the new status, current_step, results, and errors to the database within the same transaction.
2. WHEN the status field is updated, THE Job model SHALL accept only values from the WorkflowState enumeration: "pending", "running", "completed", "failed", or "cancelled".
3. WHEN results are written to the Job record, THE Job model SHALL serialize the results list to JSON and store it in the results_json column.
4. WHEN errors are written to the Job record, THE Job model SHALL serialize the errors list to JSON and store it in the errors_json column.
5. WHEN the Job record is updated, THE Job model SHALL set the updated_at timestamp to the current UTC time.

### Requirement 3: Bidirectional Model Conversion

**User Story:** As a workflow engine consumer, I want the repository to convert between the database model and the engine model seamlessly, so that persistence is transparent to the execution layer.

#### Acceptance Criteria

1. WHEN to_context is called with a Job record, THE WorkflowRepository SHALL return a WorkflowContext with state, current_step, results, and errors fields populated from the Job record.
2. WHEN sync_from_context is called with a Job record and a WorkflowContext, THE WorkflowRepository SHALL persist the context state, current_step, results, and errors back to the Job record.
3. FOR ALL valid Job records, converting to WorkflowContext and syncing back SHALL produce a Job record with equivalent state, current_step, results, and errors values (round-trip property).

### Requirement 4: Workflow Retrieval and Listing

**User Story:** As a platform operator, I want to retrieve individual workflows by ID and list workflows optionally filtered by status, so that I can monitor the system.

#### Acceptance Criteria

1. WHEN a valid workflow_id is provided, THE WorkflowRepository SHALL return the matching Job record.
2. WHEN a non-existent workflow_id is provided, THE WorkflowRepository SHALL return None.
3. WHEN list_all is called without a status filter, THE WorkflowRepository SHALL return all Job records ordered by created_at descending.
4. WHEN list_all is called with a status filter, THE WorkflowRepository SHALL return only Job records matching the specified status, ordered by created_at descending.

### Requirement 5: Workflow Resume Support

**User Story:** As a platform operator, I want to resume a failed workflow from its last successful step, so that I do not lose progress when transient errors occur.

#### Acceptance Criteria

1. WHEN a workflow in "failed" state is re-executed, THE Workflow_API SHALL load the persisted WorkflowContext and determine the number of completed steps from the results list length.
2. WHEN resuming a failed workflow, THE Workflow_API SHALL skip the number of steps equal to the count of previously completed results.
3. WHEN resuming a failed workflow, THE Workflow_API SHALL clear the errors list and reset the state to "pending" before passing the context to the WorkflowEngine.
4. WHEN the resumed workflow execution completes, THE Workflow_API SHALL persist the final WorkflowContext back to the Job record via sync_from_context.

### Requirement 6: Conflict Detection for Terminal Workflows

**User Story:** As a platform operator, I want the system to reject re-execution of workflows that are already completed or cancelled, so that I do not accidentally overwrite final results.

#### Acceptance Criteria

1. WHEN a workflow in "completed" state is submitted for execution, THE Workflow_API SHALL return HTTP status 409 with detail "Workflow already completed".
2. WHEN a workflow in "cancelled" state is submitted for execution, THE Workflow_API SHALL return HTTP status 409 with detail "Workflow was cancelled".
3. WHEN a workflow in "pending" or "failed" state is submitted for execution, THE Workflow_API SHALL proceed with execution without returning an error.

### Requirement 7: Workflow Status Retrieval via API

**User Story:** As an API consumer, I want to query the current state of a workflow by its ID, so that I can poll for completion or detect failures.

#### Acceptance Criteria

1. WHEN a GET request is made to /workflows/{workflow_id}/status with a valid ID, THE Workflow_API SHALL return a JSON response containing workflow_id and state fields.
2. WHEN a GET request is made to /workflows/{workflow_id}/status with a non-existent ID, THE Workflow_API SHALL return HTTP status 404 with detail "Workflow not found".

### Requirement 8: Job Model Schema

**User Story:** As a developer, I want the Job model to have a well-defined schema with timestamps, so that records are traceable and auditable.

#### Acceptance Criteria

1. THE Job model SHALL define columns: id (String 36, primary key), name (String 255, not null), status (String 50, not null, default "pending"), payload (Text, nullable), current_step (Integer, not null, default 0), results_json (Text, nullable), errors_json (Text, nullable), created_at (DateTime), and updated_at (DateTime).
2. THE Job model SHALL inherit from TimestampedModel which provides id, created_at, and updated_at columns automatically.
3. WHEN the results property is read from a Job with null or empty results_json, THE Job model SHALL return an empty list.
4. WHEN the errors property is read from a Job with null or empty errors_json, THE Job model SHALL return an empty list.

### Requirement 9: Database Session Management

**User Story:** As a developer, I want the WorkflowRepository to manage its own database session lifecycle, so that callers do not leak connections.

#### Acceptance Criteria

1. WHEN a WorkflowRepository is instantiated without a session argument, THE WorkflowRepository SHALL lazily create a session from SessionLocal on first access.
2. WHEN a WorkflowRepository is instantiated with an explicit session argument, THE WorkflowRepository SHALL use the provided session for all operations.
3. WHEN close is called on a WorkflowRepository, THE WorkflowRepository SHALL close the underlying session and set the internal reference to None.
