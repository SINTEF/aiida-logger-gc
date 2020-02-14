"""pytest fixtures for simplified testing."""
from __future__ import absolute_import
import pytest
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture(scope='function', autouse=True)
def clear_database_auto(clear_database):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""
@pytest.fixture(scope='function')
def logger_code(aiida_local_code_factory):
    """Get a logger code.
    """
    logger_code = aiida_local_code_factory(executable='diff',
                                           entry_point='logger')
    return logger_code
