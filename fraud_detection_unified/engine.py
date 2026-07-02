"""
Consolidated Fraud Detection Engine

Combines ML-based fraud scoring (M-Pesa) and rules-based detection (AML) into a unified interface.
"""

import pandas as pd
import joblib
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class FraudAlert:
    """Standardized fraud alert format."""
    transaction_id: str
    detected_type: str  # "ML_FRAUD", "AML_RULE", "VELOCITY", "PEP", "STRUCTURING"
    risk_score: float  # 0.0 to 1.0
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    rules_triggered: List[str]
    timestamp: str
    institution: str
    alert_message: str


class ConsolidatedFraudDetectionEngine:
    """
    Unified fraud detection combining:
    - ML-based fraud scoring for M-Pesa (transaction-level)
    - Rules-based AML detection for banking institutions (account-level)
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Args:
            config: Optional configuration dict with paths to ML models, rule definitions, etc.
        """
        self.config = config or {}
        self.ml_model = self._load_ml_model()
        self.rules_config = self._load_rules_config()
        self.alerts_log = []

    def _load_ml_model(self):
        """Load ML fraud model if available."""
        model_path = self.config.get(
            "model_path",
            "fraud_detection_unified/models/fraud_model_v1.joblib"
        )
        if os.path.exists(model_path):
            try:
                return joblib.load(model_path)
            except Exception as e:
                print(f"Warning: Could not load ML model from {model_path}: {e}")
        return None

    def _load_rules_config(self):
        """Load configurable rules thresholds."""
        return {
            "velocity_threshold_60s": self.config.get("velocity_threshold_60s", 10),
            "high_value_threshold": self.config.get("high_value_threshold", 500000),
            "structuring_threshold": self.config.get("structuring_threshold", 900000),
            "structuring_limit": self.config.get("structuring_limit", 1000000),
            "structuring_min_count": self.config.get("structuring_min_count", 3),
            "ml_fraud_threshold": self.config.get("ml_fraud_threshold", 0.7),
        }

    def score_mobile_money_transaction(self, txn: Dict[str, Any]) -> FraudAlert:
        """
        Score an M-Pesa transaction using ML model + velocity rules.

        Args:
            txn: Transaction dict with keys:
                - txn_id: Transaction identifier
                - amount: Transaction amount (KES)
                - velocity_60s: Transaction count in last 60 seconds
                - sim_swap_days: Days since SIM swap (-1 if unknown)
                - timestamp: ISO timestamp
                - institution: "MPESA" or similar

        Returns:
            FraudAlert with risk assessment.
        """
        rules_triggered = []
        risk_score = 0.0

        # Rule 1: Velocity check
        if txn.get("velocity_60s", 0) > self.rules_config["velocity_threshold_60s"]:
            rules_triggered.append("EXTREME_VELOCITY")
            risk_score += 0.25

        # Rule 2: SIM swap + high value
        if (txn.get("sim_swap_days", -1) >= 0 and
            txn.get("sim_swap_days", 999) < 2 and
            txn.get("amount", 0) > 50000):
            rules_triggered.append("HIGH_VALUE_POST_SIM_SWAP")
            risk_score += 0.20

        # Rule 3: Night transactions
        try:
            timestamp = datetime.fromisoformat(txn.get("timestamp", ""))
            if timestamp.hour < 5 or timestamp.hour > 22:
                rules_triggered.append("NIGHT_TRANSACTION")
                risk_score += 0.10
        except (ValueError, TypeError):
            pass

        # ML Model scoring (if available)
        if self.ml_model:
            features = self._extract_ml_features(txn)
            try:
                ml_prob = self.ml_model.predict_proba([features])[0][1]
                rules_triggered.append(f"ML_SCORE_{ml_prob:.2f}")
                risk_score = max(risk_score, ml_prob)
            except Exception as e:
                print(f"ML scoring error: {e}")

        # Determine severity
        severity = self._calculate_severity(risk_score, rules_triggered)

        return FraudAlert(
            transaction_id=txn.get("txn_id", "UNKNOWN"),
            detected_type="MPESA_FRAUD" if risk_score > 0.5 else "NORMAL",
            risk_score=min(risk_score, 1.0),
            severity=severity,
            rules_triggered=rules_triggered,
            timestamp=datetime.now().isoformat(),
            institution=txn.get("institution", "MPESA"),
            alert_message=self._format_alert_message(
                txn, risk_score, rules_triggered
            )
        )

    def score_banking_transaction(self, txn: Dict[str, Any]) -> FraudAlert:
        """
        Score a banking transaction using AML rules (structuring, PEP, etc.).

        Args:
            txn: Transaction dict with keys:
                - txn_id: Transaction identifier
                - account_id: Account identifier
                - amount: Transaction amount (KES)
                - txn_type: "Cash Deposit", "Transfer", etc.
                - is_pep: Boolean, Politically Exposed Person flag
                - timestamp: ISO timestamp
                - institution: Bank name

        Returns:
            FraudAlert with AML risk assessment.
        """
        rules_triggered = []
        risk_score = 0.0

        # Rule 1: High-value PEP transaction
        if txn.get("is_pep", False) and txn.get("amount", 0) > self.rules_config["high_value_threshold"]:
            rules_triggered.append("PEP_HIGH_VALUE")
            risk_score += 0.30

        # Rule 2: Structuring detection (near-limit deposits)
        if (txn.get("txn_type") == "Cash Deposit" and
            self.rules_config["structuring_threshold"] <= txn.get("amount", 0) < self.rules_config["structuring_limit"]):
            rules_triggered.append("NEAR_STRUCTURING_LIMIT")
            risk_score += 0.15

        # Rule 3: Velocity for same account
        if txn.get("recent_txn_count_48h", 0) >= self.rules_config["structuring_min_count"]:
            if txn.get("txn_type") == "Cash Deposit":
                rules_triggered.append("RAPID_CASH_DEPOSITS")
                risk_score += 0.25

        severity = self._calculate_severity(risk_score, rules_triggered)

        return FraudAlert(
            transaction_id=txn.get("txn_id", "UNKNOWN"),
            detected_type="AML_ALERT" if risk_score > 0.5 else "NORMAL",
            risk_score=min(risk_score, 1.0),
            severity=severity,
            rules_triggered=rules_triggered,
            timestamp=datetime.now().isoformat(),
            institution=txn.get("institution", "UNKNOWN_BANK"),
            alert_message=self._format_alert_message(
                txn, risk_score, rules_triggered
            )
        )

    def _extract_ml_features(self, txn: Dict) -> List[float]:
        """Extract features for ML model."""
        return [
            float(txn.get("amount", 0)),
            float(txn.get("velocity_60s", 0)),
            float(txn.get("sim_swap_days", -1)),
            1.0 if self._is_night_transaction(txn.get("timestamp")) else 0.0
        ]

    def _is_night_transaction(self, timestamp_str: str) -> bool:
        """Check if transaction occurred during night hours."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return timestamp.hour < 5 or timestamp.hour > 22
        except (ValueError, TypeError):
            return False

    def _calculate_severity(self, risk_score: float, rules: List[str]) -> str:
        """Map risk score to severity level."""
        if risk_score >= 0.9:
            return "CRITICAL"
        elif risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"

    def _format_alert_message(
        self, txn: Dict, risk_score: float, rules: List[str]
    ) -> str:
        """Format human-readable alert message."""
        institution = txn.get("institution", "UNKNOWN")
        txn_id = txn.get("txn_id", "UNKNOWN")
        amount = txn.get("amount", "?")

        rules_str = ", ".join(rules) if rules else "None"

        return (
            f"[{institution}] Txn {txn_id}: Amount {amount} KES, "
            f"Risk {risk_score:.2%} | Rules: {rules_str}"
        )

    def log_alert(self, alert: FraudAlert) -> None:
        """Log fraud alert for audit trail."""
        self.alerts_log.append(asdict(alert))

    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts."""
        if not self.alerts_log:
            return {"total_alerts": 0, "by_severity": {}}

        df = pd.DataFrame(self.alerts_log)
        return {
            "total_alerts": len(df),
            "by_severity": df["severity"].value_counts().to_dict(),
            "by_type": df["detected_type"].value_counts().to_dict(),
            "recent_critical": df[df["severity"] == "CRITICAL"]
            .to_dict(orient="records")
            if "CRITICAL" in df["severity"].values else []
        }

    def export_alerts(self, output_path: str) -> None:
        """Export alerts log to CSV."""
        if self.alerts_log:
            df = pd.DataFrame(self.alerts_log)
            df.to_csv(output_path, index=False)
            print(f"Exported {len(df)} alerts to {output_path}")
