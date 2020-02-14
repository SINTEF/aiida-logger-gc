"""
Fixtures for the logger calculations.

-----------------------------------

Here we set up different pytest fixtures that are used to represent various logger
calculations on which one can for instance test parsing etc.
"""
# pylint: disable=unused-import,unused-argument,redefined-outer-name
from __future__ import absolute_import
import pytest

# houses aiida_local_code_factory among others
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture(scope='function')
def logger_code(aiida_local_code_factory):
    """Get the premod code."""
    logger_code = aiida_local_code_factory(executable='logger',
                                           entry_point='logger')
    return logger_code
