"""
Calculations provided by aiida_logger.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""
from __future__ import absolute_import

from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.plugins import DataFactory


class LoggerCalculation(CalcJob):
    """
    AiiDA calculation plugin to fetch files from datafiles.

    Currently relies on a dummy calculation where the input files are retrieved as output files.
    In the future the extraction of data from various loggers and data sources might be possible
    using this calculation framework.
    """
    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(LoggerCalculation, cls).define(spec)
        spec.input('parameters', valid_type=DataFactory('dict'), help='Parameters to use for the processing of datafiles.')
        spec.input('verbose',
                   valid_type=DataFactory('bool'),
                   required=False,
                   default=DataFactory('bool')(False),
                   help="""
                   If True, enable more detailed output during workchain execution.
                   """)
        spec.input_namespace('datafiles', valid_type=DataFactory('singlefile'), dynamic=True, help='A dictionary of datafiles to be analyzed.')

        spec.output('data', valid_type=DataFactory('array'), help='The output data.')
        spec.output('metadata', valid_type=DataFactory('dict'), help='The output metadata.')

        spec.exit_code(1000, 'ERROR_MISSING_OUTPUT_FILE', message='Could not locate the output file.')
        spec.exit_code(1001, 'ERROR_READING_OUTPUT_FILE', message='Could not read the output file.')
        spec.exit_code(1002, 'ERROR_INVALID_CONTENT_IN_OUTPUT_FILE', message='Data format is unknown and could not be parsed.')
        spec.exit_code(1003, 'ERROR_NO_RETRIEVED_FOLDER', message='Could not obtain the retrieved folder.')
        spec.exit_code(1004, 'ERROR_MISSING_OUTPUT_FILES', message='Could not locate any of the required output files.')


    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        local_copy_list = []
        retrieve_list = []
        # Define which datafiles to analyze
        for item in self.inputs.datafiles.values():
            local_copy_list.append((item.uuid, item.filename, item.filename))
            retrieve_list.append(item.filename)
        calcinfo.local_copy_list = local_copy_list
        calcinfo.retrieve_list = retrieve_list

        return calcinfo
