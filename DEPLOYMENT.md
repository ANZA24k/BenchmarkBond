# Exact-source Studionet deployment and live verification

**Network:** stable Studionet, chain ID `61999`, `https://studio.genlayer.com/api`. Do **not** substitute `studio-dev` (chain ID `61997`). Use Studio's built-in test account; do not connect MetaMask or expose keys. Test GEN is not redeemable production payment.

## Validation

1. On the exact source commit: `python -m unittest discover -s tests -v`, `genvm-lint check contracts/benchmarkbond.py` and `python -m py_compile contracts/benchmarkbond.py`.
2. Calculate `sha256sum contracts/benchmarkbond.py` and pin this result, plus the GitHub commit, **before** deploying. Avoid redeploying unchanged source.
3. In [GenLayer Studio](https://studio.genlayer.com/), select stable **Studionet**, open contract `contracts/benchmarkbond.py`, set constructor string to the exact contents of `fixtures/protocol.json` **without its trailing newline**, then deploy with the built-in test account. Wait for **finished successful execution**, not merely pending/finalized metadata.
4. Register `submit(manifest_json)` using the exact string in `evidence/manifest.json` (remove the trailing newline). Record returned submission ID and the confirmed transaction.
5. Call `evaluate(submission_id)` with Full Consensus enabled; do not use a leader-only or mock mode. Await finalized successful execution; call `get_revision(id, 0)` and independently recompute `sha256(canonical decision JSON) == decision_hash`.
6. Query `get_protocol`, `get_submission`, `get_revision`, and `get_accounting`; collect contract/transaction Explorer URLs and verify deployed source bytes match the pinned commit. Do not guess addresses, hashes, outcomes, or successful calls. Commit these in `evidence/live-verification.md` only after direct verification.

SDK/CLI alternative when a properly authorized Studio-provided signer is available: `genlayer network set studionet` and `genlayer deploy --contract contracts/benchmarkbond.py --args "$(tr -d '\n' < fixtures/protocol.json)"`. An RPC URL alone cannot sign a transaction. Do not use a random wallet or private key extracted from a browser.

## Data and receipt model

`fixtures/protocol.json` is the constructor input. `evidence/manifest.json` pins two public fixture files to an immutable Git commit and authenticates SHA-256 plus byte length. Submission IDs start at 1. A `VERIFIED` assessment is a **possible** expected outcome of the synthetic fixture, not a predetermined or claimed network result. A partial/invalid/inconclusive outcome can be valid if validators identify methodology weaknesses.

See current official docs: [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [Web Access](https://docs.genlayer.com/developers/intelligent-contracts/features/web-access), [Testing](https://docs.genlayer.com/api-references/genlayer-test), [GenVM linter](https://docs.genlayer.com/api-references/genlayer-linter), and [Networks](https://docs.genlayer.com/developers/networks).
