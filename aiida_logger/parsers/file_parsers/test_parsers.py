""" Tests to check parsing of generic datafiles

"""
# pylint: disable=unused-import
from __future__ import print_function
from __future__ import absolute_import

import numpy as np

from aiida.plugins import CalculationFactory, DataFactory

from aiida_logger.utils.fixtures.data import fixture_retrieved  # noqa: F401


def test_generic_gc_parsing(fixture_retrieved):  # noqa: F811
    """Test a gc datafile with a comment section, labels, time and floats."""
    from aiida_logger.parsers.file_parsers.gc import GCParser

    dummy_calculation = CalculationFactory('arithmetic.add')
    exit_codes = dummy_calculation.exit_codes

    parameters = DataFactory('dict')(dict={
        'type':
        'gc',
        'comment_line':
        0,
        'data_start_line':
        2,
        'data_layout': [[{
            'time': '%m/%d/%y %H:%M:%S'
        }, {
            'id': 'int'
        }, {
            'He concentration': 'float'
        }, {
            'H2 concentration': 'float'
        }, {
            'O2 concentration': 'float'
        }, {
            'N2 concentration': 'float'
        }, {
            'CH4 concentration': 'float'
        }, {
            'CO concentration': 'float'
        }, {
            'ignore': 'float'
        }, {
            'He area': 'float'
        }, {
            'H2 area': 'float'
        }, {
            'O2 area': 'float'
        }, {
            'N2 area': 'float'
        }, {
            'CH4 area': 'float'
        }, {
            'CO area': 'float'
        }],
                        [{
                            'time': '%m/%d/%y %H:%M:%S'
                        }, {
                            'id': 'int'
                        }, {
                            'CO2 concentration': 'float'
                        }, {
                            'H2O concentration': 'float'
                        }, {
                            'ignore': 'float'
                        }, {
                            'CO2 area': 'float'
                        }, {
                            'H2O area': 'float'
                        }]],
        'separator':
        '\t',
    })

    gc_parser = GCParser(fixture_retrieved, 'gc_example.txt', exit_codes,
                         parameters)
    result = gc_parser.parse()
    data = result['data']
    metadata = result['metadata'].get_dict()

    assert 'start_time' in metadata
    assert 'labels' in metadata
    assert 'comments' in metadata
    assert metadata['labels'] == [['He concentration', 'H2 concentration', 'O2 concentration', 'N2 concentration', 'CH4 concentration', 'CO concentration', 'He area', 'H2 area', 'O2 area', 'N2 area', 'CH4 area', 'CO area'], ['CO2 concentration', 'H2O concentration', 'CO2 area', 'H2O area']]
    assert metadata['comments'] == None
    test_array = np.array([[1.67940000e+00, 5.30499200e+02, 1.01360000e+00, 5.01270000e+00,
                            1.79290000e+00, 1.31270000e+00, 4.81157000e+05, 5.63774800e+06,
                            5.34600000e+03, 6.81400000e+03, 6.41225000e+05, 2.86470000e+05],
                           [2.03480000e+00, 4.68857000e+01, 6.76100000e-01, 2.60000000e+00,
                            3.03790000e+00, 3.00000000e+00, 4.47750000e+04, 4.32223080e+07,
                            1.56494000e+05, 5.00000000e+00, 8.11070000e+04, 2.00000000e+00],
                           [3.95690000e+00, 4.61128900e+02, 6.00000000e+00, 4.00000000e+00,
                            4.64040000e+00, 3.09260000e+00, 7.12950000e+05, 4.08505819e+08,
                            3.00000000e+00, 4.00000000e+00, 9.12864000e+05, 4.66342600e+06],
                           [4.04320000e+00, 4.72441000e+01, 6.84600000e-01, 4.00000000e+00,
                            2.05930000e+00, 5.00250000e+00, 5.78310000e+04, 3.85849600e+06,
                            2.37953000e+05, 3.00000000e+00, 4.30150000e+04, 5.74000000e+02],
                           [5.98640000e+00, 6.61407300e+02, 5.10400000e+00, 6.00000000e+00,
                            6.85040000e+00, 4.88030000e+00, 6.50328000e+05, 4.90000150e+07,
                            1.79270000e+04, 1.00000000e+00, 2.02969900e+06, 8.19799000e+05],
                           [6.04560000e+00, 6.72249000e+01, 0.00000000e+00, 6.00000000e+00,
                            8.06700000e+00, 3.03250000e+00, 7.78050000e+04, 3.28244070e+07,
                            1.00000000e+00, 1.00000000e+00, 3.72850000e+04, 1.67500000e+03],
                           [7.98970000e+00, 6.61008500e+02, 7.00000000e+00, 9.00000000e+00,
                            1.31780000e+00, 5.71760000e+00, 5.54532000e+05, 8.90829209e+09,
                            2.00000000e+00, 6.00000000e+00, 2.28981500e+06, 8.86354000e+05]])
    np.testing.assert_allclose(data.get_array('channel_1'), test_array)
    test_array = np.array([[6.763590e+01, 6.672400e+00, 3.569060e+05, 5.135330e+05],
                           [1.054000e+00, 8.536100e+00, 4.834000e+04, 5.545181e+06],
                           [2.647100e+00, 8.790090e+01, 5.776000e+03, 6.738000e+03],
                           [3.061300e+00, 4.528800e+00, 5.216600e+04, 8.658100e+04],
                           [6.312000e-01, 8.868000e-01, 8.564457e+06, 7.721000e+03],
                           [2.064600e+00, 5.518600e+00, 1.390600e+04, 6.180700e+04],
                           [6.746800e+00, 3.891000e+00, 3.151360e+05, 5.453800e+04]])
    np.testing.assert_allclose(data.get_array('channel_2'), test_array)
