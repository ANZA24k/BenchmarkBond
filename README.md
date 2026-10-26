# BenchmarkBond

**Independently adjudicate a benchmark claim against an immutable evaluation protocol and commit-pinned evidence using GenLayer consensus.**

BenchmarkBond is a **standalone GenLayer Intelligent Contract**. It does not need a frontend, wallet connector, external server, database, escrow, or privileged oracle. The creator locks benchmark terms **at deployment** (dataset and version; integer-unit metrics and tolerances; paired-trial minimum; methodology; hardware/runtime; allowed deviations; forbidden shortcuts; and evidence rules). A submitter registers GitHub raw commit-pinned `report` and `runs` JSON files with exact byte lengths and SHA-256. Anyone can trigger a consensus evaluation.

### Verifiable behavior

1. `__init__(protocol_json)` permanently binds the canonical protocol and its SHA-256.
2. `submit(manifest_json)` registers a unique, immutable evidence commitment and returns a submission ID. Both required sources must use HTTPS raw GitHub URLs **pinned to a 40-hex commit SHA**; a third `methodology` source is optional.
3. `evaluate(id)` independently re-fetches and authenticates bytes inside each leader and validator's nondeterministic execution. The contract first reconciles every paired trial to the claimed candidate and baseline integer metrics. The LLM assesses methodology, comparability, exclusions, cherry-picking, and disallowed shortcuts against the locked protocol. Validator nodes independently re-fetch **and re-assess** and must agree on the canonical outcome and evidence fingerprint; leader quotes are checked against validator-fetched bytes.
4. Results are `VERIFIED`, `PARTIAL`, `INVALID`, or `INCONCLUSIVE`. Each finalized record contains the protocol/manifest hashes, independent source commitment digest, accepted evidence excerpt, reason, transaction timestamp, a deterministic `decision_hash`, and its previous hash. `get_revision(id, revision)` reads the audit chain.
5. `revise(id, new_manifest_json)` allows only the original submitter to append up to three new evidence revisions after an evaluation, unless already `VERIFIED`. No result may be overwritten; identical manifests cannot be replayed across submissions.

**Validity scope:** the contract verifies **consistency with a declared protocol and published, hashed evidence**; it does not prove that a self-published dataset was honestly collected, that the model was not trained on test data, or that synthetic results represent real performance. Source identity and scientific truth require external provenance. Full Consensus, not a successful unit test, is required to establish a deployed verdict.

### Public synthetic demo

- Protocol: [fixtures/protocol.json](fixtures/protocol.json)
- Claimed aggregate measurements: [fixtures/report.json](fixtures/report.json)
- Five paired trial measurements: [fixtures/runs.json](fixtures/runs.json)
- Commit-pinned, hashed source descriptors: [evidence/manifest.json](evidence/manifest.json)

The synthetic fixture reports candidate accuracy of **8000 bp** against baseline **6000 bp** over five paired examples, with all individual samples present. This is illustrative data and **not a genuine model performance benchmark**. The locked protocol's methodology must still be assessed semantically by GenLayer before a `VERIFIED` result can be claimed.

### API

| Method | Type | Behavior |
| --- | --- | --- |
| `get_protocol()` | view | Immutable canonical protocol JSON |
| `submit(manifest_json)` | write | Append a submission ID, reject duplicate manifests |
| `evaluate(submission_id)` | write | Consensus-based adjudication of current revision |
| `revise(submission_id, manifest_json)` | write | Append a limited new revision, only original submitter |
| `get_submission(submission_id)` | view | Submitter and revision |
| `get_revision(submission_id, revision)` | view | Manifest, verdict receipt, decision hash |
| `get_accounting()` | view | All-zero non-custodial accounting |

JSON strings must be **ASCII-escaped canonical JSON** (Python's `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)`), with duplicate keys rejected. Each source must be UTF-8, at most **8192 bytes**, and combined sources at most **16384 bytes**. Numeric report measurements and all trial measurements use **signed bounded integers**, not floats. Reported means must match raw sums within the protocol's explicitly locked per-metric `tolerance_units` (absolute integer units). Each run has the same candidate and baseline metric names, guaranteeing a paired comparison; semantic fairness still requires validator judgment.

### Development

```sh
python -m unittest discover -s tests -v
python -m py_compile contracts/benchmarkbond.py
pip install genvm-linter
genvm-lint check contracts/benchmarkbond.py
```

The offline harness verifies deterministic transitions and simulates validator disagreement; it **does not exercise GenVM**. Official linter/SDK checks run on GitHub Actions, and actual **Full Consensus must be verified independently** on Studionet with transaction and state evidence. Do not assume deployment merely because CI is green.

See [DEPLOYMENT.md](DEPLOYMENT.md), [SECURITY.md](SECURITY.md), and [evidence/live-verification.md](evidence/live-verification.md).

### Why GenLayer?

Neither a conventional smart contract nor a single chatbot can independently inspect **public immutable source bytes** and reach a network-backed qualitative judgment about fairness, cherry-picking, or benchmark methodology. GenLayer's nondeterministic web/LLM operations under the **Equivalence Principle** allow separate validators to refetch evidence and challenge the leader's assessment before an append-only verdict enters contract state.
