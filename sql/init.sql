CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS documents (
 id BIGSERIAL PRIMARY KEY, tenant TEXT NOT NULL, title TEXT NOT NULL,
 content TEXT NOT NULL, embedding vector(3), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS documents_tenant_idx ON documents(tenant);
CREATE TABLE IF NOT EXISTS jobs (
 id UUID PRIMARY KEY, tenant TEXT NOT NULL, user_id TEXT NOT NULL,
 idempotency_key TEXT NOT NULL, request_hash TEXT NOT NULL,
 payload JSONB NOT NULL, status TEXT NOT NULL DEFAULT 'queued'
 CHECK (status IN ('queued','running','completed','failed')),
 attempts INTEGER NOT NULL DEFAULT 0,
 lease_until TIMESTAMPTZ, available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 result JSONB, error TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(tenant,user_id,idempotency_key)
);
CREATE INDEX IF NOT EXISTS jobs_claim_idx ON jobs(status,available_at,lease_until);
INSERT INTO documents (tenant,title,content,embedding)
SELECT 'alpha','Campaign conversion','Delivered 10000; opened 4200; clicked 950; approved applications 80','[0.8,0.1,0.1]'::vector
WHERE NOT EXISTS (SELECT 1 FROM documents WHERE tenant='alpha' AND title='Campaign conversion');
INSERT INTO documents (tenant,title,content,embedding)
SELECT 'beta','Beta private report','Beta delivered 5000; clicked 450','[0.1,0.8,0.1]'::vector
WHERE NOT EXISTS (SELECT 1 FROM documents WHERE tenant='beta' AND title='Beta private report');
