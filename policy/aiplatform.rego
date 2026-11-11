package aiplatform

import rego.v1

default allow := false

allow if {
  input.action == "read"
  input.tenant == input.resource.tenant
  input.resource.scope in input.scopes
  input.resource.type in {"campaign", "risk", "analysis"}
}

allow if {
  input.action == "submit"
  input.tenant == input.resource.tenant
  input.resource.scope == "campaign:read"
  "campaign:read" in input.scopes
  input.resource.type == "analysis"
}
