# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/config.py: Handles the modules configuration

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import json

from .const import CONFIG_FN
from .errors import config_parser_error
from .lib import generate_session_id


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def echo_parameter(param_name):

	print(get_module_config()[param_name])


def get_default_config():

	return dict(
		id = generate_session_id(), # Generate unique session id
		stdout = True, # Display messages from stdout
		stderr = True, # Display messages from stderr
		log_write = False, # Write log messages into file
		log_level = 0, # Overall log level: No logs are generated by default
		arch = 'win32', # Define Wine & Wine-Python architecture
		version = '3.5.3', # Define Wine-Python version
		dir = __get_default_config_directory__(), # Default config directory
		)


def get_module_config(override_dict = None):

	# Default override_dict is empty
	if override_dict is None:
		override_dict = {}

	# Get config from files as a prioritized list
	config = __locate_and_read_config_files__()

	# Add override parameters
	config.insert(0, override_dict)

	# Add defaults
	config.append(get_default_config())

	# Sort and return the config
	return __join_config_by_priority__(config)


def __get_default_config_directory__():

	return os.path.join(os.path.expanduser('~'), CONFIG_FN)


def __join_config_by_priority__(config_dict_list):

	# Gather all the keys ...
	key_set = set()
	for config_dict in config_dict_list:
		key_set = key_set | set(list(config_dict.keys()))

	# New parameter dict
	parameter_dict = {}

	# Go through list, from low priority to high
	for config_dict in reversed(config_dict_list):

		# Go through keys
		for key in key_set:

			# Change config is needed
			if key in config_dict.keys():
				parameter_dict[key] = config_dict[key]

	return parameter_dict


def __locate_and_read_config_files__():

	# List of config files' contents by priority
	config_dict_list = []

	# Look for config in the usual spots
	for file_location in [
		os.getcwd(),
		os.environ.get('ZUGBRUECKE'),
		__get_default_config_directory__(),
		'/etc/zugbruecke'
		]:

		# If there is a path ...
		if file_location is None:
			continue

		# Compile path
		try_path = os.path.join(file_location, CONFIG_FN)

		# Is this a file?
		if not os.path.isfile(try_path):
			continue

		# Read file
		try:
			with open(try_path, 'r', encoding = 'utf-8') as f:
				cnt = f.read()
		except:
			raise config_parser_error('Config file could not be read: "%s"' % try_path)

		# Try to parse it
		try:
			config_dict_list.append(json.loads(cnt))
		except:
			raise config_parser_error('Config file could not be parsed: "%s"' % try_path)

	return config_dict_list
