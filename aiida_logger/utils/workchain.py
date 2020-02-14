"""
Utils for the workchains.

------------------------
"""
from __future__ import absolute_import
from aiida.engine.processes.exit_code import ExitCode


def compose_exit_code(status, message):
    """Compose an ExitCode instance based on a status and message."""
    exit_code = ExitCode(status=status, message=message)
    return exit_code
