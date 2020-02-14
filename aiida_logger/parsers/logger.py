# -*- coding: utf-8 -*-
"""
Parsers provided by aiida_logger.

Register parsers via the "aiida.parsers" entry point in setup.json.
"""
from __future__ import absolute_import

from aiida.common import exceptions
from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

from aiida_logger.parsers.file_parsers.gc import GCParser

class LoggerParser(Parser):
    """
    Parser class for parsing output of calculation.
    """
    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a LoggerCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        super(LoggerParser, self).__init__(node)
        if not issubclass(node.process_class, CalculationFactory('logger')):
            raise exceptions.ParsingError("Can only parse LoggerCalculation")

    def parse(self, **kwargs):  # pylint: disable=too-many-locals
        """
        Parse outputs, store results in database.

        :returns: an exit code, if parsing fails (or nothing if parsing succeeds)
        """

        import fleep
        from aiida.common.links import LinkType

        # Check if retrieved folder is present
        try:
            output_folder = self.retrieved
        except exceptions.NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # Check that folder content is as expected
        files_retrieved = output_folder.list_object_names()
        inputs = self.node.get_incoming(link_type=LinkType.INPUT_CALC).nested()
        files_expected = inputs['datafiles']
        files_expected = [item.filename for item in files_expected.values()]
        # Note: set(A) <= set(B) checks whether A is a subset of B
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to find '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES
        if len(files_expected) > 1:
            raise NotImplementedError('Only one file is currently supported for parsing.')
        filename=files_expected[0]
        parameters = inputs['parameters']
        gc_parser = GCParser(output_folder, filename, self.exit_codes, parameters)
        result = gc_parser.parse()
        if isinstance(result, dict):
            self.out('data', result['data'])
            self.out('metadata', result['metadata'])
        else:
            # Assume we have an exit code
            return result

        return ExitCode(0)
