"""Escalate-only semantic/multilingual tier for claim classification.

This module is a small public wrapper around claim_gate.py's semantic classifier.
Use classify_escalating() where a host wants the extra tier. The keyword floor is
never downgraded; semantic rules only add a class when the floor is silent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from claim_gate import classify_escalating_content, classify_semantic_content  # noqa: E402


def classify_semantic(path, text):
    return classify_semantic_content(path, text)


def classify_escalating(path, text):
    return classify_escalating_content(path, text)
