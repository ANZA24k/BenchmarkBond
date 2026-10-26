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
| Canonical *repository* source SHA-256 (not deployed) | `784b014f35f458e14205f4c65fcc6a85bdebf909a06cdb3ef8cac492874475e3` |

Public source fixtures are intentionally **synthetic**. Validated byte commitments demonstrate reproducible document identity, not that the benchmark is representative of any real model. The report lists all five paired trials and zero exclusions.

To verify, follow [DEPLOYMENT.md](../DEPLOYMENT.md). Record the Explorer receipt outcome, GenVM execution status, leader/validator consensus result, contract address, all transaction hashes, decision hash checked against the canonical receipt, stored revisions, and zero-balance accounting. Never report an attempted or pending transaction as finalized.

## Confirmed build evidence (not chain verification)

- Exact contract: [`contracts/benchmarkbond.py`](https://github.com/ANZA24k/BenchmarkBond/blob/0a1492f31b5d4a04a41a0ef1c982b865460d2ae0/contracts/benchmarkbond.py); repository file's Git blob SHA-1 matches the locally tested file (`b62f9fd2f6ad86c4a2fcfc0948c319ba0dba9b05`).
- [GitHub Actions success](https://github.com/ANZA24k/BenchmarkBond/actions/runs/40302709600) at commit `4e5a8ef91b4b8a2243a1664b3dc39dc3129d1378`: `genvm-lint check`, 13 offline unit tests and `py_compile` all successful. This is **not** a Full Consensus or StudioNet deployment.
- Fixture snapshot commit: [`291f4ee4805d05e816c8489c6181c50ee1064cda`](https://github.com/ANZA24k/BenchmarkBond/tree/291f4ee4805d05e816c8489c6181c50ee1064cda/fixtures). Report SHA-256: `19f9a36215cfde479c3c6803716ef5bdb65ce2d7b0784ae97a90eca946733f4e` (738 bytes); runs SHA-256: `2df8fee3f1fa60e215df1bd50ac615d3cc095424c3bc07a6c51cd8ebde48a7f4` (457 bytes).
