"""
EstimatePerformance workchain

-----------------------------
Estimate the performance based on example spreadsheet and gc data.
"""

# pylint: disable=attribute-defined-outside-init
from aiida.common.extendeddicts import AttributeDict
from aiida.engine import calcfunction, WorkChain, append_
from aiida.plugins import DataFactory, CalculationFactory

from aiida_logger.utils.workchain import compose_exit_code


class GCExampleWorkChain(WorkChain):
    """Use gc data and perform a few example calculations."""

    _verbose = False
    _calculation_string = 'logger'
    _calculation = CalculationFactory(_calculation_string)

    @classmethod
    def define(cls, spec):
        super(GCExampleWorkChain, cls).define(spec)
        spec.expose_inputs(cls._calculation, exclude=['parameters', 'metadata'])
        #spec.expose_inputs(cls._calculation, include=['metadata'], namespace='calc')
        spec.input('options', valid_type=dict, required=False)
        spec.input('parameters', valid_type=DataFactory('dict'), help='Parameters for the calculations')
        spec.input('verbose',
                   valid_type=DataFactory('bool'),
                   required=False,
                   default=lambda: DataFactory('bool')(False),
                   help="""
                   If True, enable more detailed output during workchain execution.
                   """)

        spec.outline(
            cls.initialize,
            cls.init_get_gc_data,
            cls.get_gc_data,
            cls.verify_calculation,
            cls.process_gc_data,
            cls.finalize
        )  # yapf: disable
        spec.output('concentration_data', valid_type=DataFactory('array'), required=False, help='The concentration data calculated from the area using the supplied calibration values')
        
        spec.expose_outputs(cls._calculation)

        spec.exit_code(0, 'NO_ERROR', message='the sun is shining')
        spec.exit_code(420, 'ERROR_NO_CALLED_CALCULATION', message='no called calculation detected')
        spec.exit_code(500, 'ERROR_UNKNOWN', message='unknown error detected in the workchain')

    def initialize(self):
        """Initialize."""
        self._init_context()
        self._init_inputs()

    def _init_context(self):
        """Initialize context variables that are used during the logical flow."""
        self.ctx.exit_code = self.exit_codes.ERROR_UNKNOWN  # pylint: disable=no-member
        self.ctx.inputs = AttributeDict()

    def _init_inputs(self):
        """Initialize inputs."""
        try:
            self._verbose = self.inputs.verbose.value
            self.ctx.inputs.verbose = self.inputs.verbose
        except AttributeError:
            pass

        # Set metadata as this is similar between runs
        self.ctx.inputs.metadata = {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1},
                                                'parser_name': 'logger',
                                                'withmpi': False,
                                                'output_filename': 'logger.out'}}

    def init_get_gc_data(self):
        """Initialize the get unit data."""
        try:
            self.ctx.inputs
        except AttributeError:
            raise ValueError('No input dictionary was defined in self.ctx.inputs')
        
        # Add exposed inputs
        self.ctx.inputs.update(self.exposed_inputs(self._calculation))

        # Add necessary additional inputs
        parameters_input = self.inputs.parameters.get_dict()['gc']
        self.ctx.calibration_data = parameters_input.pop('calibration', None)
        parameters = DataFactory('dict')(dict=parameters_input)
        self.ctx.inputs.parameters = parameters

    def get_gc_data(self):
        """Get the gc data."""
        inputs = self.ctx.inputs
        running = self.submit(self._calculation, **inputs)

        self.report('fetching gc data using {}<{}> '.format(self._calculation.__name__, running.pk))

        return self.to_context(calculations=append_(running))

    def verify_calculation(self):
        """Verify calculation."""

        try:
            calculation = self.ctx.calculations[-1]
        except IndexError:
            self.report('There is no {} in the called calculation list.'.format(self._calculation.__name__))
            return self.exit_codes.ERROR_NO_CALLED_CALCULATION  # pylint: disable=no-member

        # Inherit exit status from last calculation (supposed to be
        # successfull)
        next_calculation_exit_status = calculation.exit_status
        next_calculation_exit_message = calculation.exit_message
        if not next_calculation_exit_status:
            self.ctx.exit_code = self.exit_codes.NO_ERROR  # pylint: disable=no-member
        else:
            self.ctx.exit_code = compose_exit_code(next_calculation_exit_status, next_calculation_exit_message)
            self.report('The called {}<{}> returned a non-zero exit status. '
                        'The exit status {} is inherited'.format(calculation.__class__.__name__, calculation.pk, self.ctx.exit_code))

        return self.ctx.exit_code

    def process_gc_data(self):
        """Process data from the unit and the gc and estimate performance."""
        gc_data = self.ctx.calculations[0]

        # First calculate the concentration from the area using calibrated values for all channels
        data = gc_data.outputs.data

        calibration_data = DataFactory('list')(list=self.ctx.calibration_data)
        concentration_data = calculate_concentration_from_area(self.ctx.inputs.parameters, calibration_data, data)
    
        self.out('concentration_data', concentration_data)
        
    def finalize(self):
        """Finalize the calculation."""
        calculation = self.ctx.calculations[-1]
        self.out_many(self.exposed_outputs(calculation, self._calculation))


@calcfunction
def calculate_concentration_from_area(parameters_data, calibration_data, data):
    import numpy as np
    """Calculate the concentration from the area and the calibration."""
    channels = [item for item in data.get_arraynames() if item != 'time' and item != 'id']
    parameters = parameters_data.get_dict()
    start_slice = 0
    concentration_data = DataFactory('array')()
    for index, channel in enumerate(channels):
        calibration = []
        calibration_species = []
        for item in calibration_data[index]:
            calibration.append(list(item.values())[0])
            calibration_species.append(list(item.keys())[0] + ' area')
        calibration = np.array(calibration)
        slicing_index = 0
        for index, item in enumerate(parameters['data_layout'][index]):
            if 'concentration' in list(item.keys())[0]:
                slicing_index = slicing_index + 1
        area = data.get_array(channel)
        # concentration = area x calibration
        concentration = area[:,slicing_index::] * calibration
        concentration_data.set_array(channel, concentration)
    return concentration_data
