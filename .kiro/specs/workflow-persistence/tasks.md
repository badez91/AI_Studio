# Implementation Plan: Workflow Persistence

## Overview

This plan implements durable workflow state persistence for AI Studio using SQLAlchemy and SQLite. The implementation follows a layered architecture: Job model (ORM) → WorkflowRepository (data access) → API Router (REST endpoints), with bidirectional conversion between the database model and the in-memory WorkflowContext used by the engine. Property-based tests using Hypothesis validate correctness properties defined in the design.

## Tasks

- [x] 1. Set up Job model and database schema
  - [x] 1.1 Create the Job model with JSON serialization
    - Define `Job` class in `app/models/job.py` inheriting from `TimestampedModel`
    - Add columns: name (String 255), status (String 50, default "pending"), payload (Text, nullable), current_step (Integer, default 0), results_json (Text, nullable), errors_json (Text, nullable)
    - Implement `results` and `errors` properties with JSON serialization/deserialization
    - Handle NULL/empty JSON columns by returning empty lists
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 2.3, 2.4_

- [x] 2. Implement WorkflowRepository
  - [x] 2.1 Create WorkflowRepository with CRUD operations
    - Implement `create(name, payload?)` to generate UUID v4 and persist a pending Job
    - Implement `get(workflow_id)` to retrieve by primary key, returning None if not found
    - Implement `update_state(job, state, current_step?, results?, errors?)` to persist state changes
    - Implement `list_all(status?)` with optional filtering and descending created_at ordering
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.5, 4.1, 4.2, 4.3, 4.4_

  - [x] 2.2 Implement bidirectional conversion methods
    - Implement `to_context(job)` converting Job → WorkflowContext
    - Implement `sync_from_context(job, context)` persisting WorkflowContext → Job
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 2.3 Implement session management
    - Support lazy session creation from SessionLocal when no session provided
    - Support explicit session injection via constructor
    - Implement `close()` to release session and set reference to None
    - Use late import pattern to avoid circular dependencies
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 3. Integrate API router with persistence
  - [x] 3.1 Replace in-memory storage with WorkflowRepository in API endpoints
    - Update `POST /workflows` to use `repo.create()` and return workflow_id
    - Update `GET /workflows/{id}/status` to use `repo.get()` with 404 handling
    - Update `POST /workflows/{id}/execute` to load Job, run engine, and persist results
    - Ensure `repo.close()` is called in `finally` blocks for all endpoints
    - _Requirements: 7.1, 7.2, 1.3_

  - [x] 3.2 Implement resume logic in execute endpoint
    - Detect failed state via `to_context()` conversion
    - Calculate completed step count from `len(context.results)`
    - Skip completed steps by slicing the steps list
    - Clear errors and reset state to pending before engine execution
    - Persist final context via `sync_from_context()`
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 3.3 Implement conflict detection
    - Check for "completed" status → return HTTP 409 "Workflow already completed"
    - Check for "cancelled" status → return HTTP 409 "Workflow was cancelled"
    - Allow execution for "pending" and "failed" states
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 4. Write repository and interface tests
  - [x] 4.1 Write repository unit tests
    - Test create workflow (initial state verification)
    - Test get workflow (existing and non-existent IDs)
    - Test update_state (status, current_step, results, errors persistence)
    - Test to_context and sync_from_context conversion
    - Test list_all with and without status filter
    - Test resume scenario (failed workflow state reconstruction)
    - Use in-memory SQLite database with test fixture
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 3.2, 4.3, 4.4, 5.1_

  - [x] 4.2 Write API integration tests
    - Test full submit → execute → status flow via TestClient
    - Test 404 for non-existent workflow status query
    - Test 409 conflict detection (execute completed workflow twice)
    - _Requirements: 6.1, 7.1, 7.2_

- [x] 5. Checkpoint - Verify core implementation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Property-based tests with Hypothesis
  - [ ] 6.1 Write property test for Creation Invariant
    - **Property 1: Creation Invariant**
    - Generate random workflow names and optional payloads using `st.text()` and `st.none() | st.text()`
    - Verify created Job has valid 36-char UUID, status "pending", current_step 0, results `[]`, errors `[]`
    - Verify created Job is retrievable by its ID
    - Use in-memory SQLite for isolation
    - Minimum 100 iterations
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [ ] 6.2 Write property test for JSON Serialization Round-Trip
    - **Property 2: JSON Serialization Round-Trip**
    - Generate random JSON-serializable lists using `st.lists(st.one_of(st.text(), st.integers(), st.floats(allow_nan=False), st.booleans()))`
    - Assign to `job.results` and `job.errors`, read back and verify equality
    - **Validates: Requirements 2.3, 2.4**

  - [ ] 6.3 Write property test for State Update Persistence
    - **Property 3: State Update Persistence**
    - Generate random valid WorkflowState via `st.sampled_from(WorkflowState)`, current_step via `st.integers(min_value=0, max_value=100)`, results and errors lists
    - Call `update_state()`, then re-read Job from DB and verify all values match
    - **Validates: Requirements 2.1**

  - [ ] 6.4 Write property test for Bidirectional Conversion Round-Trip
    - **Property 4: Bidirectional Conversion Round-Trip**
    - Create Jobs with various valid states, convert to WorkflowContext via `to_context()`, sync back via `sync_from_context()`
    - Verify resulting Job has equivalent status, current_step, results, and errors
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [ ] 6.5 Write property test for List Filtering Correctness
    - **Property 5: List Filtering Correctness**
    - Create N jobs with random statuses from `st.lists(st.sampled_from(WorkflowState))`
    - Verify `list_all(status=S)` returns only matching jobs
    - Verify `list_all()` returns all jobs ordered by created_at descending
    - **Validates: Requirements 4.3, 4.4**

  - [ ] 6.6 Write property test for Resume Skip Correctness
    - **Property 6: Resume Skip Correctness**
    - Generate failed workflows with K completed results and N total steps (K < N)
    - Verify resume executes exactly N-K steps, clears errors, resets state to pending
    - Use `st.integers(min_value=0, max_value=10)` for K and N
    - **Validates: Requirements 5.1, 5.2, 5.3**

  - [ ] 6.7 Write property test for Conflict Detection
    - **Property 7: Conflict Detection for Terminal States**
    - Generate workflows in each WorkflowState via `st.sampled_from(WorkflowState)`
    - Verify terminal states (completed, cancelled) return HTTP 409
    - Verify non-terminal states (pending, failed) do NOT return HTTP 409
    - Use FastAPI TestClient for endpoint testing
    - **Validates: Requirements 6.1, 6.2, 6.3**

  - [ ] 6.8 Write property test for Status Endpoint Correctness
    - **Property 8: Status Endpoint Correctness**
    - Create workflows with random names, query status endpoint, verify response has workflow_id and state
    - Generate non-existent UUIDs via `st.uuids()`, verify 404 response
    - **Validates: Requirements 7.1, 7.2**

- [ ] 7. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `[x]` are already implemented in the codebase
- Tasks 1–5 reflect the existing implementation across `app/models/job.py`, `app/storage/workflow_repository.py`, `app/api/router.py`, `tests/test_workflow_persistence.py`, and `tests/test_interfaces.py`
- Task 6 (Property-based tests) is pending — these use Hypothesis as specified in the design document
- Each property test should be placed in `tests/test_workflow_pbt.py`
- Property tests validate universal correctness properties from the design document
- Use in-memory SQLite databases in fixtures for test isolation
- Minimum 100 iterations per property test as specified in the design

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["6.1", "6.2"] },
    { "id": 1, "tasks": ["6.3", "6.4", "6.5"] },
    { "id": 2, "tasks": ["6.6", "6.7", "6.8"] }
  ]
}
```
