# Deployment Profiles

The canonical spec defines an enterprise-grade pipeline. Requiring the full enterprise stack to get *any* value was this pack's biggest weakness — profiles fix that. **Same schemas, same gates, same BLOCKED codes in every profile.** Only the connector and detector *implementations* change; the contract never does.

| | reference | standard | enterprise |
|---|---|---|---|
| Input formats | text / markdown | + PDF, DOCX, PPTX, XLSX, HTML (Tika) | + portal retrieval (Playwright) |
| PII detector | regex ruleset (`REFERENCE_EU_PII_V1`) | regex or Presidio | Presidio services (EU config) |
| Secrets detector | regex ruleset (`REFERENCE_SECRETS_V1`) | Gitleaks CLI | Gitleaks + org rulesets |
| Sources | local files (manual import) | + SharePoint/Drive exports | + vendor portals w/ legal-basis gates |
| ACLs | sentinel `acl://reference/local-single-user` | source-system refs | propagated end-to-end |
| Retention/GDPR | raw deleted immediately + proof | same | + retention exception gates, legal-basis records |
| Publish target | local `sanitized/` dir | file store | sanitized store + search index |
| Infra required | **none** | Tika server, Gitleaks binary | + Presidio, session store, K8s-grade ops |
| Status | **shipped, 24 tests green** | build target | build target |

## Rules that hold across all profiles

1. **Gate parity.** A profile may strengthen a detector, never remove an enforcement point. All three sensitive-data passes run in every profile.
2. **Sentinel values are explicit, not defaults.** Where a field doesn't apply (ACLs on a single-user laptop), the config carries a *visible sentinel* (`acl://reference/local-single-user`), never an empty string or a silently-invented value. Auditors can grep for sentinels.
3. **Conformance fixtures are profile-independent.** `./verify.sh` must pass against any profile's implementation of scope, labeling, quality, and chunking — the algorithms are normative, the infrastructure is not.
4. **Degrade path is explicit.** If Tika is down in standard profile: `BLOCKED: tika_unavailable` — you may still ingest text files (reference-profile behavior), you may not silently skip parsing. If a portal breaks in enterprise profile: manual file import (reference behavior) is the sanctioned fallback — see [OPERATIONS.md](OPERATIONS.md).

## Choosing

- Evaluating the approach, building a personal/team knowledge store, CI-validating the spec → **reference**.
- Real document formats, real secrets engine, still no compliance officers → **standard**.
- Vendor portals, GDPR jurisdiction, ACL-bearing sources, audit requirements → **enterprise** (this is what the spec was written for; use the build-pack flow in [PACKAGE-OVERVIEW.md](PACKAGE-OVERVIEW.md)).
