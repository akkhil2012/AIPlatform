"""PostgreSQL pgvector retrieval and leased durable job queue."""
import hashlib,json,os,uuid
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

DATABASE_URL=os.getenv("DATABASE_URL","postgresql://aiplatform:aiplatform@postgres:5432/aiplatform")

@contextmanager
def connection():
    with psycopg.connect(DATABASE_URL,row_factory=dict_row) as db:
        yield db

def retrieve(tenant:str,vector:list[float],limit:int=3):
    if len(vector)!=3: raise ValueError("Demo embedding must have exactly 3 dimensions")
    embedding="["+ ",".join(str(float(v)) for v in vector)+"]"
    with connection() as db:
        return db.execute("""SELECT id,title,content,updated_at FROM documents
          WHERE tenant=%s AND embedding IS NOT NULL
          ORDER BY embedding <=> %s::vector LIMIT %s""",(tenant,embedding,min(limit,10))).fetchall()

def submit_job(tenant,user_id,key,payload):
    if not key or len(key)>160: raise ValueError("Invalid idempotency key")
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    with connection() as db:
        row=db.execute("""INSERT INTO jobs (id,tenant,user_id,idempotency_key,request_hash,payload)
            VALUES (%s,%s,%s,%s,%s,%s::jsonb)
            ON CONFLICT (tenant,user_id,idempotency_key) DO UPDATE
            SET updated_at=jobs.updated_at
            RETURNING id,request_hash,status""",(str(uuid.uuid4()),tenant,user_id,key,digest,json.dumps(payload))).fetchone()
        if row["request_hash"]!=digest: raise ValueError("Idempotency key reused with different payload")
        return {"id":str(row["id"]),"status":row["status"]}

def get_job(tenant,user_id,job_id):
    with connection() as db:
        return db.execute("""SELECT id,status,result,error,attempts FROM jobs
            WHERE id=%s AND tenant=%s AND user_id=%s""",(job_id,tenant,user_id)).fetchone()

def claim_job(max_attempts=3):
    with connection() as db:
        return db.execute("""WITH candidate AS (
            SELECT id FROM jobs
            WHERE ((status='queued' AND available_at<=now())
               OR (status='running' AND lease_until<now()))
            AND attempts < %s
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED LIMIT 1
        )
        UPDATE jobs SET status='running', attempts=jobs.attempts+1,
          lease_until=now()+interval '90 seconds', updated_at=now()
        FROM candidate WHERE jobs.id=candidate.id
        RETURNING jobs.*""",(max_attempts,)).fetchone()

def finish_job(job_id,result=None,error=None,max_attempts=3):
    with connection() as db:
        if error is None:
            db.execute("""UPDATE jobs SET status='completed',result=%s::jsonb,
               lease_until=NULL,updated_at=now() WHERE id=%s""",(json.dumps(result),job_id))
        else:
            db.execute("""UPDATE jobs SET status=CASE WHEN attempts >= %s THEN 'failed' ELSE 'queued' END,
               error=%s, available_at=now()+interval '15 seconds',
               lease_until=NULL,updated_at=now() WHERE id=%s""",(max_attempts,str(error)[:500],job_id))
