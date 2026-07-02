"""
Consolidated Fraud Detection Engine

Unified fraud detection module supporting:
- M-Pesa real-time transaction fraud scoring (ML-based)
- Banking sector AML rule-based detection (structuring, PEP, velocity)
- Configurable rules engine for multiple institution types

Architecture: Registry pattern allows adding detection engines per institution.
"""

from .engine import ConsolidatedFraudDetectionEngine

__all__ = ["ConsolidatedFraudDetectionEngine"]
