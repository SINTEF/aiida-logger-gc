from __future__ import absolute_import

from __future__ import print_function
from aiida.plugins import DataFactory
from dateutil import parser
import numpy as np

from aiida_logger.parsers.file_parsers.base import BaseFileParser
from six.moves import range


class GCParser(BaseFileParser):  # pylint: disable=too-many-locals
    """Parser class for parsing data from gas chromatographs."""
    def __init__(self, *args, **kwargs):
        super(GCParser, self).__init__(*args, **kwargs)

    def _parse(self, file_handle):  # pylint: disable=too-many-locals
        """Parse the content of GC file as a NumPy array."""

        # Set the separator
        try:
            separator = self.parameters['separator']
        except KeyError:
            separator = ' '

        # Fetch comment and label ranges
        try:
            comment_range = self.parameters['comment_range']
        except KeyError:
            comment_range = None

        # Read content
        content = file_handle.readlines()
        comments = None
        labels = None
        separator = self.parameters['separator']

        # Fetch data layout
        data_layout = self.parameters['data_layout']

        # Fetch comments if specified
        shift_index = 0
        if comment_range:
            if '-' not in comment_range and ',' not in comment_range:
                # Only comments on one line
                comments = content[int(self.parameters['comment_range'])]
                shift_index = shift_index + 1
            else:
                raise NotImplementedError

        date_time = []
        sample_id = []
        labels = []
        data = []
        time_index = []
        id_index = []
        ignore_index = []
        num_channels = len(data_layout)
        num_fields = []
        for channel in range(num_channels):
            data.append([])
            fields = 0
            for index, item in enumerate(data_layout[channel]):
                if 'time' in item:
                    time_index.append([index])
                elif 'id' in item:
                    id_index.append([index])
                elif 'ignore' in item:
                    ignore_index.append([index])
                else:
                    fields = fields + 1
            num_fields.append(fields)
            # Build labels
            labels.append(
                [list(item.keys())[0] for item in data_layout[channel] if list(item.keys())[0] != 'time' and list(item.keys())[0] != 'id' and list(item.keys())[0] != 'ignore'])
        # Check that only one time index is given
        if True in [len(item) > 1 for item in time_index]:
            raise ValueError(
                'More than one time entry per channel. Please correct the configuration.'
            )
        # Make sure we only have integers in the list (find a more clever way to do this)
        time_index = [item[0] for item in time_index]

        # Check that only one id index is given
        if True in [len(item) > 1 for item in id_index]:
            raise ValueError(
                'More than one id entry per channel. Please correct the configuration.'
            )
        # Make sure we only have integers in the list (find a more clever way to do this)
        id_index = [item[0] for item in id_index]

        # Start extracting the actual data
        for line in content[self.parameters['data_start_line']:]:
            line = line.split(separator)
            start_channel_index = 0
            for channel in range(num_channels):
                id_ind = id_index[channel]
                time_ind = time_index[channel]
                try:
                    # Remove ignore columns, but allow not having any
                    for ignore_ind in ignore_index[channel]:
                        line.pop(start_channel_index + ignore_ind)
                        if ignore_ind < id_ind:
                            id_ind = id_ind - 1
                        if ignore_ind < time_ind:
                            time_ind = time_ind - 1
                except IndexError:
                    pass
                if id_ind > time_index[channel]:
                    id_ind = id_ind - 1
                if channel == 0:
                    # Fetch and remove time entries
                    date_time.append(
                        parser.parse(line.pop(time_index[channel]).strip(),
                                     fuzzy=True))
                    # Fetch and remove id entries (assumed the same between channels)
                    try:
                        s_id = int(line.pop(id_ind).strip())
                    except ValueError:
                        s_id = 0
                    sample_id.append(s_id)
                else:
                    # For the other channels, remove time and id data
                    line.pop(start_channel_index + time_index[channel])
                    line.pop(start_channel_index + id_ind)
                # Convert from string to target data for each channel
                try:
                    data[channel].append([
                        float(item) for index, item in enumerate(
                            line[start_channel_index:start_channel_index +
                                 num_fields[channel]])
                    ])
                except ValueError as e:
                    raise ValueError('A field with an empty string might have been detected. Are you sure you have '
                                     'specified correct ignore fields in the parameters?') from e

                start_channel_index = start_channel_index + num_fields[channel]
        # Calculate time difference for each step and store that instead of absolute times
        reference_time = date_time[0]
        date_time = [(time - reference_time).total_seconds()
                     for time in date_time]
        # Compose data, time and metadata nodes
        array_data = DataFactory('array')()
        for channel in range(num_channels):
            array_data.set_array('channel_'+str(channel + 1), np.array(data[channel]))
        array_data.set_array('time', np.array(date_time))
        array_data.set_array('id', np.array(sample_id[channel]))
        meta = DataFactory('dict')(dict={
            # Consider to replace the string conversion in the future
            # problem is that we also need timzone information.
            'start_time': str(reference_time.utcnow()),
            'comments': comments,
            'labels': labels
        })
        return {'data': array_data, 'metadata': meta}
