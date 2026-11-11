"""Postgres-leased background worker; retries and idempotent submission.

At-least-once execution: LLM calls can repeat after a lease expires. Do not
attach non-idempotent external side effects without an outbox/receipt protocol.
"""
import logging,os,time
from enterprise.db import claim_job,finish_job,retrieve
from llm import ask

logging.basicConfig(level=logging.INFO)
log=logging.getLogger("worker")

def process(job):
    tenant=job["tenant"]
    prompt=job["payload"]["question"]
    # Derive evidence only from the job's trusted persisted tenant.
    docs=retrieve(tenant,[0.8,0.1,0.2],3)
    evidence=[{"title":d["title"],"content":d["content"]} for d in docs]
    result=ask("Summarize only supplied synthetic tenant evidence. Never invent metrics.",
               str({"question":prompt,"evidence":evidence}))
    return {"answer":result,"evidence_ids":[str(d["id"]) for d in docs]}

def main():
    while True:
        try:
            job=claim_job()
            if job is None:
                time.sleep(2)
                continue
            try:
                result=process(job)
                finish_job(job["id"],result=result)
            except Exception as exc:
                log.exception("Job failed: %s",job["id"])
                finish_job(job["id"],error=str(exc))
        except Exception:
            log.exception("Worker polling error")
            time.sleep(5)

if __name__=="__main__": main()
