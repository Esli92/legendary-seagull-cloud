# encoding: utf-8

"""

Abstractions for parsing observation files and standard implementations.

"""

from __future__ import absolute_import, division, print_function, unicode_literals
from importlib import import_module
import re
from util.utilities import whLogger


LOG = whLogger(__name__)


class InsufficientHeaders(ValueError):
    """
    There was insufficient information in header lines to configure the parser
    to accept data lines.
    """
    pass


class ObservationParser(object):
    """
    This class is an abstraction of parsers for observational weather data.
    Data is assumed to be organized as a series of text strings, usually lines
    in a text file, with zero or more header lines and subsequent lines
    containing observations.

    Concrete ObservationParsers are created, and then lines from the beginning
    of the input data are passed to `parse_header_line` until it returns False
    to indicate that it is not a header. Implementations can use various
    methods for deciding this such as looking for marker characters, counting
    lines, consulting the stars or calling a friend.

    The `parse_file_name` method may also be called before any header lines
    are parsed, with the name of the input file the data is taken from. This
    allows any meta-data to be retrieved from the file-name.

    After all header lines have been consumed, the meta field may have been
    populated with meta-data from the header and the parser should be
    configured to accept data lines. Otherwise, InsufficientHeaders is raised.

    Finally, all subsequent lines are passed to `parse_data_line` which returns
    a `dict` of observations. It may also return `None` if no observations were
    found or if they need to be accumulated over multiple lines in complex
    cases.

    Finally, `end_input` is called, which may return a `dict` to be imported
    and which will reset the parser so it can receive new header lines.
    """

    def __init__(self):
        super(ObservationParser, self).__init__()
        self.meta = {}

    def parse_file_name(self, path):
        """
        Parse input file-name to accumulate meta-data.

        :param path: The file-name or path.
        :type path: string
        :rtype: None
        """
        pass

    def parse_header_line(self, line):
        """
        Parse header line.

        :param line: Line from beginning of input, which may be header data.
        :type line: string
        :return: Whether the line was header data.
        :rtype: bool
        """
        return False

    def parse_data_line(self, line):
        """
        Parse data line.

        :param line: Line from body of input
        :type line: string
        :return: Observations found in line, if any
        :rtype: dict or None
        """
        return None

    def end_input(self):
        """
        Finish accepting lines to the current self.data.
        Convert self.data to a (observation) list.
        Reset parser so that it can accept new data.
        Return observation list.
        """
        return None

    def parse_sequence(self, input, ignore_broken_lines=False):
        """
        Parses a sequence of lines, by calling `parse_header_line`,
        `parse_data_line` and `end_input` as appropriate.

        :type input: iterable of string
        :param input: Source of lines to import
        :rtype: list of dict
        :returns: A list of observations returned by `parse_data_line` and `end_input`
        """
        observations = []
        input = iter(input)
        for line in input:
            if not self.parse_header_line(line):
                LOG.debug('Not header = %s', line)

                try:
                    from_line = self.parse_data_line(line)
                except:
                    if ignore_broken_lines:
                        from_line = None
                    else:
                        raise

                #from_line = self.parse_data_line(line)
                if from_line is not None:
                    observations.append(from_line)
                break
            else:
                LOG.debug('Header = %s', line)
        for line in input:
            try:
                from_line = self.parse_data_line(line)
            except:
                if ignore_broken_lines:
                    from_line = None
                else:
                    raise
            if from_line is not None:
                observations.append(from_line)
        from_end = self.end_input()
        if from_end is not None:
            observations.append(from_end)
        return observations

    def get_metadata(self):
        return self.meta


class SeparatedTextObservationParser(ObservationParser):
    """
    An abstract ObservationParser which reads files with values separated by
    a regexp. Concrete sub-classes may want to implement `parse_header_line`
    to populate the `field_list` property or initialise it in the constructor.

    The separator and field_list must be initialised before parse_data_line is
    called.
    """

    def __init__(self, separator=None, field_list=None, headers=None):
        super(SeparatedTextObservationParser, self).__init__()

        self.separator = re.compile(separator) if separator else None
        """
        Regular expression to split lines on.
        :type: __Regex
        """

        self.headers = re.compile(headers) if headers else None
        """
        Regular expression to recognize header lines
        :type: __Regex
        """

        self.field_list = field_list or []
        """
        List of fields to pick from lines after splitting, as tuples of (name, converter, idx0, ..., idxN)
        """

    def parse_header_line(self, line):
        if line == '':
            return True
        if self.headers:
            return self.headers.match(line)
        return False

    def parse_data_line(self, line):
        if line is None or line == '':
            return None
        parts = self.separator.split(line)
        obs = {}
        for field in self.field_list:
            params = None
            try:
                params = tuple(parts[idx] for idx in field[2:])
                value = field[1](*params)
                #if value is not None:
                obs[field[0]] = value
            except:
                LOG.exception('%s Failed to parse %s out of %s in %s', type(self).__name__, field[0], params or field[2:], line)
                raise
        return obs


PARSER_MODULES = ('parser',
                  'parser.belgingur',
                  'parser.landsverk_fo',
                  'parser.vegagerdin',
                  'parser.landsvirkjun',
                  'parser.vedurstofan',
                  'parser.cabo_verde',
                  'parser.africa',
                  'parser.basic',)


def find_parser(name, onerror=None):
    for module_name in PARSER_MODULES:
        try:
            module = import_module(module_name)
            klass = getattr(module, name)
            if klass is not None:
                return klass
        except:
            pass
    msg = '%s not found in %s' % (name, ', '.join(PARSER_MODULES))
    if onerror:
        onerror(msg)
    else:
        raise ValueError(msg)
