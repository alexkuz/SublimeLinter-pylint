#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by NotSqrt
# Copyright (c) 2013 NotSqrt
#
# License: MIT
#

"""This module exports the Pylint plugin class."""

import os
from SublimeLinter.lint import PythonLinter, util, persist


class Pylint(PythonLinter):

    """Provides an interface to pylint."""

    syntax = 'python'
    cmd = (
        'pylint',
        '--msg-template=\'{line}:{column}:{msg_id}: {msg}\'',
        '--module-rgx=.*',  # don't check the module name
        '--reports=n',      # remove tables
        '--persistent=n',   # don't save the old score (no sense for temp)
    )
    version_args = '--version'
    version_re = r'^pylint.* (?P<version>\d+\.\d+\.\d+),'
    version_requirement = '>= 1.0'
    regex = (
        r'^(?P<line>\d+):(?P<col>\d+):'
        r'(?:(?P<error>[RFE])|(?P<warning>[CIW]))\d+: '
        r'(?P<message>.*)'
    )
    multiline = True
    line_col_base = (1, 0)
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDOUT  # ignore missing config file message
    defaults = {
        '--disable=,': '',
        '--enable=,': '',
        '--rcfile=': ''
    }
    inline_overrides = ('enable', 'disable')
    check_version = True

    def split_match(self, match):
        """
        Return the components of the error message.

        We override this to deal with the idiosyncracies of pylint's error messages.

        """

        match, line, col, error, warning, message, near = super().split_match(match)

        if match:
            if col == 0:
                col = None

        return match, line, col, error, warning, message, near

    def merge_rc_settings(self, settings):
        """
        Merge .sublimelinterrc settings with settings.

        Searches for .sublimelinterrc in, starting at the directory of the linter's view.
        The search is limited to rc_search_limit directories. If found, the meta settings
        and settings for this linter in the rc file are merged with settings.

        """

        search_limit = persist.settings.get('rc_search_limit', self.RC_SEARCH_LIMIT)
        rc_settings = util.get_view_rc_settings(self.view, limit=search_limit)

        if rc_settings:
            meta = self.meta_settings(rc_settings)
            rc_settings = rc_settings.get('linters', {}).get(self.name, {})
            rc_settings.update(meta)
            rcfile = rc_settings.get('rcfile')
            if rcfile:
                start_dir = os.path.dirname(self.view.file_name())
                linterrc_path = util.find_file(start_dir, '.sublimelinterrc', limit=search_limit)
                linterrc_dir = os.path.dirname(linterrc_path)
                rc_settings['rcfile'] = os.path.abspath(os.path.join(linterrc_dir, rc_settings['rcfile']))
            settings.update(rc_settings)
