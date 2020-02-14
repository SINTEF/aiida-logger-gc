"""
An example script that launches the workflow to estimate the performance
of a sensor unit with a gas chromatograph connected.
"""
# pylint: disable=too-many-arguments
import os
import numpy as np
from aiida.common.extendeddicts import AttributeDict
from aiida.orm import Code, Bool, Str
from aiida.plugins import DataFactory, WorkflowFactory
from aiida.engine import run
from aiida import load_profile
load_profile()

from aiida_logger.tests import TEST_DIR  # pylint: disable=wrong-import-position

def main(code_string, datafiles, parameters):
    """Main method to setup the calculation."""

    # First, we need to fetch the AiiDA datatypes which will
    # house the inputs to our calculation
    dict_data = DataFactory('dict')

    # Then, we set the workchain we would like to call
    workchain = WorkflowFactory('logger.gc_example')

    # Set inputs for the following WorkChain execution
    inputs = AttributeDict()
    # inputs.metadata = {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1},
    #                                'parser_name': 'logger',
    #                                'withmpi': False,
    #                                'output_filename': 'logger.out'}}
    # Set code
    inputs.code = Code.get_from_string(code_string)
    # Set datafiles
    inputs.datafiles = datafiles
    # Set parameters
    inputs.parameters = dict_data(dict=parameters)
    # Set workchain related inputs, in this case, give more explicit output to report
    inputs.verbose = Bool(True)
    # Submit the requested workchain with the supplied inputs
    run(workchain, **inputs)

if __name__ == '__main__':
    # Code_string is chosen among the list given by 'verdi code list'
    CODE_STRING = 'dummy@localhost'

    # Set datafiles
    DATAFILES = {'gc': DataFactory('singlefile')(file=os.path.join(TEST_DIR, 'input_files', 'gc_example.txt'))}

    # Set parameters
    PARAMETERS = {'gc': {'type': 'gc',
                         'comment_line': 0,
                         'data_start_line': 2,
                         'data_layout': [[{'time': '%m/%d/%y %H:%M:%S'},
                                          {'id': 'int'},
                                          {'He concentration': 'float'},
                                          {'H2 concentration': 'float'},
                                          {'O2 concentration': 'float'},
                                          {'N2 concentration': 'float'},
                                          {'CH4 concentration': 'float'},
                                          {'CO concentration': 'float'},
                                          {'ignore': 'float'},
                                          {'He area': 'float'},
                                          {'H2 area': 'float'},
                                          {'O2 area': 'float'},
                                          {'N2 area': 'float'},
                                          {'CH4 area': 'float'},
                                          {'CO area': 'float'}],
                                         [{'time': '%m/%d/%y %H:%M:%S'},
                                          {'id': 'int'},
                                          {'CO2 concentration': 'float'},
                                          {'H2O concentration': 'float'},
                                          {'ignore': 'float'},
                                          {'CO2 area': 'float'},
                                          {'H2O area': 'float'}]],
                         'calibration': [[{'He': 7e-7},
                                          {'H2': 5e-7},
                                          {'O2': 1e-8},
                                          {'N2': 1e-8},
                                          {'CH4': 2e-8},
                                          {'CO': 5e-6}],
                                         [{'CO2': 2e-6},
                                          {'H2O': 5e-6}]],
                         'separator': '\t',
                         'ignore_columns': [[8], [3]],
                         'ignore_rows': []}}

    main(CODE_STRING, DATAFILES, PARAMETERS)
