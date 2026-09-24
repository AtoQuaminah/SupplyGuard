# pipeline.py
# This is the central orchestrator for SupplyGuard.
# It controls the order of scanning and decides when to exit early.
# No detection logic lives here — each layer handles its own responsibility.

from supplyguard.layers.layer1_crypto import CryptoVerification
from supplyguard.layers.layer2_behavioral import BehavioralAnalysis
from supplyguard.layers.layer3_threat_intel import ThreatIntelligence
from supplyguard.layers.layer4_ml import MLClassifier
from supplyguard.utils.logger import Logger
import time


class SupplyGuardPipeline:

    def __init__(self):
        self.layer1 = CryptoVerification()
        self.layer2 = BehavioralAnalysis()
        self.layer3 = ThreatIntelligence()
        self.layer4 = MLClassifier()
        self.logger = Logger()

    def scan(self, file_path: str) -> dict:
        print(f"\n[SupplyGuard] Scanning: {file_path}")
        print("=" * 60)

        start_time = time.time()

        # This dictionary accumulates results across all four layers.
        # It becomes the final report returned to the caller.
        scan_report = {
            "file": file_path,
            "verdict": None,
            "layers": {},
            "scan_time_seconds": None
        }

        # LAYER 1 — Cryptographic Verification
        # Establishes whether the file arrived intact and untampered.
        # The hash computed here is reused by Layer 3 for VirusTotal lookup,
        # so we avoid hashing the file twice.
        print("[Layer 1] Verifying file integrity...")
        l1 = self.layer1.run(file_path)
        scan_report["layers"]["layer1"] = l1
        self.logger.log(file_path, "Layer1", l1)
        print(f"          Hash: {l1['hash']} | Signature: {l1['status']}")

        # LAYER 2 — Behavioral Analysis
        # Inspects the file statically for structural red flags —
        # obfuscation, suspicious imports, high-entropy sections.
        # Layer 1 result is passed in so Layer 2 can factor in signature validity.
        print("[Layer 2] Analysing file behaviour...")
        l2 = self.layer2.run(file_path, l1)
        scan_report["layers"]["layer2"] = l2
        self.logger.log(file_path, "Layer2", l2)
        print(f"          Risk Score: {l2['risk_score']} | Flags: {l2['flags']}")

        # Early exit — if behavioral analysis is overwhelmingly confident,
        # there is no value in querying external APIs or running ML inference.
        # This also protects API quota and keeps scan times low.
        if l2["risk_score"] >= 0.9:
            scan_report["verdict"] = "Malicious"
            scan_report["scan_time_seconds"] = round(time.time() - start_time, 3)
            self.logger.log(file_path, "Verdict", scan_report)
            self._print_verdict(scan_report)
            return scan_report

        # LAYER 3 — Threat Intelligence
        # Checks the file hash against VirusTotal's database of 70+ AV engines.
        # Redis caching means repeated scans of the same file skip the API call entirely.
        print("[Layer 3] Checking threat intelligence...")
        l3 = self.layer3.run(file_path, l1, l2)
        scan_report["layers"]["layer3"] = l3
        self.logger.log(file_path, "Layer3", l3)
        print(f"          Reputation Score: {l3['reputation_score']} | Source: {l3['source']}")

        # Deterministic rule from the proposal — if crowd-sourced intelligence
        # already confirms the file is malicious, ML classification adds nothing.
        if l3["reputation_score"] > 0.7:
            scan_report["verdict"] = "Malicious"
            scan_report["scan_time_seconds"] = round(time.time() - start_time, 3)
            self.logger.log(file_path, "Verdict", scan_report)
            self._print_verdict(scan_report)
            return scan_report

        # LAYER 4 — ML Classification
        # LightGBM model trained on EMBER features makes the final call
        # for files that passed or were ambiguous in the previous three layers.
        # Confidence score matters here — a low-confidence Benign is still worth flagging.
        print("[Layer 4] Running ML classification...")
        l4 = self.layer4.run(file_path, l1, l2, l3)
        scan_report["layers"]["layer4"] = l4
        self.logger.log(file_path, "Layer4", l4)
        print(f"          Verdict: {l4['verdict']} | Confidence: {l4['confidence']}")

        scan_report["verdict"] = l4["verdict"]
        scan_report["scan_time_seconds"] = round(time.time() - start_time, 3)
        self.logger.log(file_path, "Verdict", scan_report)
        self._print_verdict(scan_report)
        return scan_report

    def _print_verdict(self, report: dict):
        print("=" * 60)
        print(f"[SupplyGuard] VERDICT: {report['verdict']}")
        print(f"[SupplyGuard] Completed in {report['scan_time_seconds']}s")
        print("=" * 60)