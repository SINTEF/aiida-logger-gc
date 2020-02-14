"""
Fixtures that setup fixtures to be used for testing

---------------------------------------------------

Here we set up different pytest fixtures that are used to represent various necessary
quantities that are repeated in tests related to data structures.
"""
# pylint: disable=unused-import,unused-argument,redefined-outer-name
from __future__ import absolute_import
import os
import pytest

# houses aiida_local_code_factory among others
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture(scope='function')
def fixture_retrieved():
    """Configure a retrieved folder."""
    from aiida.plugins import DataFactory
    from aiida_logger.tests import TEST_DIR

    retrieved = DataFactory('folder')()
    retrieved.put_object_from_tree(path=os.path.join(TEST_DIR, 'input_files'))

    return retrieved
