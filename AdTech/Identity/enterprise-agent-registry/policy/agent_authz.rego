package agent_authz

import rego.v1

default allow := false

allow if {

    input.identity.principal_type == "agent"

    input.identity.sub == input.agent.agent_id

    input.identity.tenant_id == input.agent.tenant_id

    input.agent.status == "ACTIVE"

    input.action in input.agent.allowed_actions
}