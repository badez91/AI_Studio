import sys
from pathlib import Path

# Ensure project root is on sys.path for direct script execution
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.api.main import create_app
from app.storage.workflow_repository import WorkflowRepository

client = TestClient(create_app())
post = client.post('/api/v1/workflows', json={'topic':'Diag Test','style':'default','duration':'1m'})
wid = post.json()['workflow_id']
print('created', wid)
exec_resp = client.post(f'/api/v1/workflows/{wid}/execute')
print('execute status', exec_resp.status_code)
print('execute body:', exec_resp.json())
repo = WorkflowRepository()
job = repo.get(wid)
print('job.status', job.status)
print('job.current_step', job.current_step)
print('job.errors', job.errors)
print('job.results', job.results)
