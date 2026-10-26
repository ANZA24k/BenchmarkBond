# BenchmarkBond live verification record

Status: **NOT YET VERIFIED ON STABLE STUDIONET**. Do not substitute a local simulation, GitHub Actions run, or a contract from an earlier build for a real Full Consensus execution. Complete this record only with direct independently confirmed data.

| Field | Current verified value |
| --- | --- |
| Repo | https://github.com/ANZA24k/BenchmarkBond |
| Network target | stable Studionet / chain ID 61999 |
| Deployed source commit | Not deployed / unverified |
| Final docs commit | Record from repository head after push |
| Contract address / Explorer | Not deployed / unverified |
| Deployment transaction | Not deployed / unverified |
| `submit` transaction | Not executed / unverified |
| `evaluate` Full Consensus transaction | Not executed / unverified |
| Submission ID | Not executed / unverified |
| Final status / decision hash | Not executed / unverified |
| Final readback / accounting | Not executed / unverified |
| Canonical source SHA-256 | Compute from exact deployed Python file before deployment |

Public source fixtures are intentionally **synthetic**. Validated byte commitments demonstrate reproducible document identity, not that the benchmark is representative of any real model. The report lists all five paired trials and zero exclusions.

To verify, follow [DEPLOYMENT.md](../DEPLOYMENT.md). Record the Explorer receipt outcome, GenVM execution status, leader/validator consensus result, contract address, all transaction hashes, decision hash checked against the canonical receipt, stored revisions, and zero-balance accounting. Never report an attempted or pending transaction as finalized.
