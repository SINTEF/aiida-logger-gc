[![Build Status](https://github.com/espenfl/aiida-logger/workflows/ci/badge.svg?branch=master)](https://travis-ci.org/espenfl/aiida-logger/actions)
[![Coverage Status](https://coveralls.io/repos/github/espenfl/aiida-logger/badge.svg?branch=master)](https://coveralls.io/github/espenfl/aiida-logger?branch=master)
[![Docs status](https://readthedocs.org/projects/aiida-logger/badge)](http://aiida-logger.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/aiida-logger.svg)](https://badge.fury.io/py/aiida-logger)

AiiDA-Logger
------------

A generic AiiDA base plugin for registering data. This can be used as a base for setting up for instance an AiiDA data logger that absorbs data ejected from an instrument.

## Installation

```shell
pip install aiida-logger
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show the calclulation plugins in AiiDA-Logger
```


## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:
```shell
verdi daemon start         # make sure the daemon is running
cd examples
verdi run example.py        # submit test calculation
verdi process list -a  # check status of calculation
```

## Development

```shell
git clone https://github.com/espenfl/aiida-logger .
cd aiida-logger
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-logger.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT


## Contact

espen.flage-larsen@sintef.no

