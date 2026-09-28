import structlog
import pytest
import io
import sys


def test_structlog_emission_info_level(capsys):
    """Ensures structlog emits structured JSON-like output at info level."""
    logger = structlog.get_logger("TestLogger")
    logger.info("test_event", key="value")

    captured = capsys.readouterr()
    assert "test_event" in captured.out
    assert "key" in captured.out
    assert "value" in captured.out


def test_structlog_emission_error_level(capsys):
    """Ensures structlog emits structured JSON-like output at error level."""
    logger = structlog.get_logger("TestLogger")
    logger.error("error_event", reason="failure")

    captured = capsys.readouterr()
    assert "error_event" in captured.out
    assert "reason" in captured.out
    assert "failure" in captured.out


def test_structlog_logger_instance():
    """Ensures structlog logger instance is created successfully."""
    logger = structlog.get_logger("AnotherLogger")
    assert logger is not None
