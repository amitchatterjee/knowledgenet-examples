import pytest
from framework import execute

def test_sanity():
    result = execute('rules', ['data'], '../target/results')
    assert result is not None


def todo_validation_rules():
    result = execute('rules', ['test/data/validation-rules'], '../target/results')
    assert result is not None
