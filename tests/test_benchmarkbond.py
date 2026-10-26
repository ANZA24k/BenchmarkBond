"""Offline contract execution harness: deterministic rules + simulated nondet consensus.

Real GenVM/Full Consensus must be separately verified; this is not a substitute.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fixture(name):
    return (ROOT / "fixtures" / name).read_bytes()


class AttrDict(dict):
    pass


class MockVM:
    class Return:
        def __init__(self, calldata):
            self.calldata = calldata

    class UserError(Exception):
        pass

    def __init__(self):
        self.fail_consensus = False
        self.calls = 0

    def run_nondet_unsafe(self, leader, validator):
        result = leader()
        self.calls += 1
        if self.fail_consensus or not validator(self.Return(result)):
            raise RuntimeError("validator rejected leader")
        return result


class MockWeb:
    def __init__(self):
        self.values = {}
        self.calls = []

    def get(self, url):
        self.calls.append(url)
        status, body = self.values[url]
        return types.SimpleNamespace(status_code=status, body=body)


class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vm = MockVM()
        cls.web = MockWeb()
        cls.sender = types.SimpleNamespace(sender_address="0xCreator")
        cls.assessment = {"outcome": "VERIFIED", "reason": "Complete paired dataset and no exclusions", "excerpt": "No samples were excluded."}
        def prompt(text, response_format=None):
            assert response_format == "json"
            return dict(cls.assessment)
        noop = lambda fn: fn
        gl = types.SimpleNamespace(Contract=object,
                                   public=types.SimpleNamespace(write=noop, view=noop),
                                   message=cls.sender, vm=cls.vm,
                                   nondet=types.SimpleNamespace(web=cls.web, exec_prompt=prompt))
        sdk = types.ModuleType("genlayer")
        sdk.gl = gl
        sdk.TreeMap = dict
        sdk.u256 = int
        sdk.Address = str
        sys.modules["genlayer"] = sdk
        spec = importlib.util.spec_from_file_location("benchmarkbond", ROOT / "contracts" / "benchmarkbond.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def setUp(self):
        self.vm.fail_consensus = False
        self.vm.calls = 0
        self.web.calls = []
        self.sender.sender_address = "0xCreator"
        self.__class__.assessment = {"outcome": "VERIFIED", "reason": "Complete paired dataset and no exclusions", "excerpt": "No samples were excluded."}
        self.contract = self.module.BenchmarkBond(fixture("protocol.json").decode().strip())
        self.urls = {}
        items = []
        for role in ("report", "runs"):
            data = fixture(role + ".json")
            url = "https://raw.githubusercontent.com/ANZA24k/BenchmarkBond/" + "a" * 40 + "/fixtures/" + role + ".json"
            self.urls[role] = url
            self.web.values[url] = (200, data)
            items.append({"role": role, "url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        self.manifest = canonical(items)

    def test_full_success_and_stable_receipt(self):
        self.sender.sender_address = "0xSubmitter"
        sub = self.contract.submit(self.manifest)
        self.sender.sender_address = "0xOther"
        self.assertEqual(self.contract.evaluate(sub), "VERIFIED")
        self.assertEqual(len(self.web.calls), 4)  # each validator independently re-fetches both
        packet = json.loads(self.contract.get_revision(sub, 0))
        receipt = packet["decision"]
        self.assertEqual(hashlib.sha256(receipt.encode()).hexdigest(), packet["decision_hash"])
        self.assertEqual(json.loads(receipt)["outcome"], "VERIFIED")
        with self.assertRaises(ValueError):
            self.contract.evaluate(sub)
        self.assertFalse(json.loads(self.contract.get_accounting())["custody_enabled"])

    def test_duplicate_manifest_and_url_validation(self):
        self.contract.submit(self.manifest)
        with self.assertRaisesRegex(ValueError, "already submitted"):
            self.contract.submit(self.manifest)
        for bad in ["http://raw.githubusercontent.com", "https://evil.example/x", "https://raw.githubusercontent.com/X/Y/" + "a" * 40 + "/../x", self.urls["report"] + "?token=1"]:
            value = json.loads(self.manifest)
            value[0]["url"] = bad
            with self.subTest(url=bad), self.assertRaises(ValueError):
                self.contract.submit(canonical(value))

    def test_duplicate_json_keys_and_noncanonical(self):
        with self.assertRaises(ValueError):
            self.module._parse_canonical('{"a":1,"a":2}', 30)
        with self.assertRaises(ValueError):
            self.contract.submit(json.dumps(json.loads(self.manifest), indent=2))

    def test_wrong_hash_and_bytes_are_invalid(self):
        sub = self.contract.submit(self.manifest)
        self.web.values[self.urls["runs"]] = (200, b"tampered")
        self.assertEqual(self.contract.evaluate(sub), "INVALID")
        self.assertIn("mismatch", self.contract.get_revision(sub, 0))

    def test_missing_evidence_inconclusive(self):
        sub = self.contract.submit(self.manifest)
        self.web.values[self.urls["runs"]] = (404, b"")
        self.assertEqual(self.contract.evaluate(sub), "INCONCLUSIVE")

    def test_transient_failure_does_not_write(self):
        sub = self.contract.submit(self.manifest)
        self.web.values[self.urls["runs"]] = (503, b"")
        with self.assertRaises(self.vm.UserError):
            self.contract.evaluate(sub)
        self.assertFalse(json.loads(self.contract.get_revision(sub, 0))["decision"])

    def test_objective_mismatch_invalid(self):
        bad = json.loads(fixture("report.json"))
        bad["candidate_metrics"]["accuracy_bp"] = 9999
        new = canonical(bad).encode()
        items = json.loads(self.manifest)
        items[0]["sha256"] = hashlib.sha256(new).hexdigest()
        items[0]["bytes"] = len(new)
        self.web.values[self.urls["report"]] = (200, new)
        sub = self.contract.submit(canonical(items))
        self.assertEqual(self.contract.evaluate(sub), "INVALID")
        self.assertIn("inconsistent", self.contract.get_revision(sub, 0))

    def test_duplicate_trial_ids_invalid(self):
        bad = json.loads(fixture("runs.json"))
        bad["observations"][1]["id"] = bad["observations"][0]["id"]
        new = canonical(bad).encode()
        items = json.loads(self.manifest)
        items[1]["sha256"] = hashlib.sha256(new).hexdigest()
        items[1]["bytes"] = len(new)
        self.web.values[self.urls["runs"]] = (200, new)
        sub = self.contract.submit(canonical(items))
        self.assertEqual(self.contract.evaluate(sub), "INVALID")

    def test_revision_permissions_history_and_replay(self):
        sub = self.contract.submit(self.manifest)
        self.web.values[self.urls["runs"]] = (404, b"")
        self.assertEqual(self.contract.evaluate(sub), "INCONCLUSIVE")
        other = json.loads(self.manifest)
        other[1]["url"] = other[1]["url"].replace("/runs.json", "/revision.json")
        other_url = other[1]["url"]
        self.web.values[other_url] = (200, fixture("runs.json"))
        revised = canonical(other)
        self.sender.sender_address = "0xAttacker"
        with self.assertRaises(ValueError):
            self.contract.revise(sub, revised)
        self.sender.sender_address = "0xCreator"
        self.assertEqual(self.contract.revise(sub, revised), 1)
        self.assertEqual(self.contract.evaluate(sub), "VERIFIED")
        first = json.loads(self.contract.get_revision(sub, 0))
        latest = json.loads(self.contract.get_revision(sub, 1))
        self.assertEqual(json.loads(latest["decision"])["previous_hash"], first["decision_hash"])
        with self.assertRaises(ValueError):
            self.contract.revise(sub, self.manifest)

    def test_validator_disagreement_no_commit(self):
        sub = self.contract.submit(self.manifest)
        self.vm.fail_consensus = True
        with self.assertRaises(RuntimeError):
            self.contract.evaluate(sub)
        self.assertEqual(json.loads(self.contract.get_revision(sub, 0))["decision"], "")

    def test_injected_model_quote_is_rejected(self):
        sub = self.contract.submit(self.manifest)
        self.__class__.assessment = {"outcome": "VERIFIED", "reason": "Trust me", "excerpt": "unverifiable model statement"}
        with self.assertRaises(self.vm.UserError):
            self.contract.evaluate(sub)

    def test_immutable_protocol_and_accounting(self):
        with self.assertRaises(ValueError):
            self.module._terms(fixture("protocol.json").decode().strip().replace('"fixture-v1"','"fixture-v1","version":"evil"'))
        self.assertEqual(self.contract.protocol_hash, hashlib.sha256(fixture("protocol.json").strip()).hexdigest())
        self.assertEqual(json.loads(self.contract.get_accounting())["liabilities"], 0)

    def test_invalid_utf8_is_invalid_not_transient(self):
        bad = b"\xff\xfe"
        items = json.loads(self.manifest)
        items[0]["sha256"] = hashlib.sha256(bad).hexdigest()
        items[0]["bytes"] = len(bad)
        self.web.values[self.urls["report"]] = (200, bad)
        sub = self.contract.submit(canonical(items))
        self.assertEqual(self.contract.evaluate(sub), "INVALID")
        self.assertIn("invalid UTF-8", self.contract.get_revision(sub, 0))


if __name__ == "__main__":
    unittest.main()
