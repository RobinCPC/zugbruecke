#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/_server_.py: Started with Python on Wine, executing DLL calls

	Required to run on platform / side: [WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
import ctypes
import os
from pprint import pformat as pf
import sys
import traceback

from lib import FUNDAMENTAL_C_DATATYPES
from log import log_class
from rpc import (
	mp_server_class
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine_server_class:


	def __init__(self, session_id, parameter):

		# Store session id and parameter
		self.id = session_id
		self.p = parameter

		# Start logging session and connect it with log on unix side
		self.log = log_class(self.id, self.p)

		# Status log
		self.log.out('[_server_] STARTING ...')

		# Mark session as up
		self.up = True

		# Start dict for dll files and routines
		self.dll_dict = {}

		# Create server
		self.server = mp_server_class(
			('localhost', self.p['port_socket_ctypes']),
			'pycrosscall_server_main',
			log = self.log,
			terminate_function = self.__terminate__
			)

		# Register call: Accessing a dll
		self.server.register_function(self.__access_dll__, 'access_dll')
		# Call routine with parameters and, optionally, return value
		self.server.register_function(self.__call_dll_routine__, 'call_dll_routine')
		# Return status of server
		self.server.register_function(self.__get_status__, 'get_status')
		# Register call: Registering arguments and return value types
		self.server.register_function(self.__register_argtype_and_restype__, 'register_argtype_and_restype')
		# Register call: Registering dll calls
		self.server.register_function(self.__register_routine__, 'register_routine')
		# Register destructur: Call goes into xmlrpc-server first, which then terminates parent
		self.server.register_function(self.server.terminate, 'terminate')

		# Status log
		self.log.out('[_server_] ctypes server is listening on port %d.' % self.p['port_socket_ctypes'])
		self.log.out('[_server_] STARTED.')
		self.log.out('[_server_] Serve forever ...')

		# Run server ...
		self.server.serve_forever()


	def __access_dll__(self, full_path_dll, full_path_dll_unix, dll_name, dll_type):

		# Although this should happen only once per dll, lets be on the safe side
		if full_path_dll not in self.dll_dict.keys():

			# Log status
			self.log.out('[_server_] Attaching to "%s" of type %s ...' % (dll_name, dll_type))
			self.log.out('[_server_]  (%s)' % full_path_dll)

			try:

				# Load library TODO do this for different types of dlls (cdll, oledll)
				self.dll_dict[full_path_dll_unix] = {
					'type': dll_type,
					'name': dll_name,
					'full_path': full_path_dll,
					'dll_handler': ctypes.windll.LoadLibrary(full_path_dll),
					'method_handlers': {},
					'method_metainfo': {}
					}

				# Log status
				self.log.out('[_server_] ... done.')

				return 1 # Success

			except:

				# Log status
				self.log.out('[_server_] ... failed! Traceback:')

				# Push traceback to log
				self.log.out(traceback.format_exc())

				return 0 # Fail

		# Just in case
		return 1


	def __call_dll_routine__(self, full_path_dll_unix, routine_name, arg_message_dict):

		# Log status
		self.log.out('[_server_] Trying call routine "%s" ...' % routine_name)

		# Make it shorter ...
		method = self.dll_dict[full_path_dll_unix]['method_handlers'][routine_name]
		method_metainfo = self.dll_dict[full_path_dll_unix]['method_metainfo'][routine_name]

		# Unpack passed arguments, handle pointers and structs ...
		args, kw = self.__unpack_arguments__(method_metainfo, arg_message_dict)

		# Default return value
		return_value = None

		# This is risky
		try:

			# Call into dll
			return_value = method(*args, **kw)

			# Log status
			self.log.out('[_server_] ... done.')

		except:

			# Log status
			self.log.out('[_server_] ... failed! Traceback:')

			# Push traceback to log
			self.log.out(traceback.format_exc())

		# Pack return package and return it
		return self.__pack_return__(method_metainfo, args, kw, return_value)


	def __get_status__(self):

		if self.up:
			return 'up'
		else:
			return 'down'


	def __pack_return__(self, method_metainfo, args, kw, return_value):

		# Start argument list as a list
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = method_metainfo['argtypes'][arg_index]

			# Handle fundamental types by value
			if not arg_definition_dict['p'] and arg_definition_dict['f']:

				# Nothing to do ...
				arguments_list.append(None)

			# Handle fundamental types by reference
			elif arg_definition_dict['p'] and arg_definition_dict['f']:

				# Append value from ctypes datatype (because most of their Python equivalents are immutable)
				arguments_list.append(arg.value)

			# Handle everything else (structures)
			else:

				# HACK TODO
				arguments_list.append(None)

		return {
			'args': arguments_list,
			'kw': {}, # TODO not yet handled
			'return_value': return_value # TODO allow & handle pointers
			}


	def __register_argtype_and_restype__(self, full_path_dll_unix, routine_name, argtypes, restype):

		# Log status
		self.log.out('[_server_] Trying to set argument and return value types for "%s" ...' % routine_name)

		# Make it shorter ...
		method = self.dll_dict[full_path_dll_unix]['method_handlers'][routine_name]
		method_metainfo = self.dll_dict[full_path_dll_unix]['method_metainfo'][routine_name]

		# Parse & store argtype dicts into argtypes
		method_metainfo['argtypes'] = argtypes
		method.argtypes = [self.__unpack_datatype_dict__(arg_dict) for arg_dict in argtypes]

		# Parse & store return value type
		method_metainfo['restype'] = restype
		method.restype = self.__unpack_datatype_dict__(restype)

		# Log status
		self.log.out('[_server_] ... argtypes: %s ...' % pf(method.argtypes))
		self.log.out('[_server_] ... restype: %s ...' % pf(method.restype))

		# Log status
		self.log.out('[_server_] ... done.')

		return 1 # Success


	def __register_routine__(self, full_path_dll_unix, routine_name):

		# Log status
		self.log.out('[_server_] Trying to access "%s"' % routine_name)

		try:

			# Just in case this routine is already known
			if routine_name not in self.dll_dict[full_path_dll_unix]['method_handlers'].keys():

				# Get handler on routine in dll
				self.dll_dict[full_path_dll_unix]['method_handlers'][routine_name] = getattr(
					self.dll_dict[full_path_dll_unix]['dll_handler'], routine_name
					)

				# Prepare dict for metainfo
				self.dll_dict[full_path_dll_unix]['method_metainfo'][routine_name] = {}

			# Log status
			self.log.out('[_server_] ... done.')

			return 1 # Success

		except:

			# Log status
			self.log.out('[_server_] ... failed! Traceback:')

			# Push traceback to log
			self.log.out(traceback.format_exc())

			return 0 # Fail


	def __terminate__(self):

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('[_server_] TERMINATING ...')

			# Terminate log
			self.log.terminate()

			# Status log
			self.log.out('[_server_] TERMINATED.')

			# Session down
			self.up = False


	def __unpack_arguments__(self, method_metainfo, arg_message_dict):

		# Start argument list as a list
		arguments_list = []

		# Get arguments' list
		args = arg_message_dict['args']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = method_metainfo['argtypes'][arg_index]

			# Handle fundamental types by value
			if not arg_definition_dict['p'] and arg_definition_dict['f']:

				# Append value
				arguments_list.append(arg)

			# Handle fundamental types by reference
			elif arg_definition_dict['p'] and arg_definition_dict['f']:

				# Put value back into its ctypes datatype
				arguments_list.append(
					getattr(ctypes, arg_definition_dict['t'])(arg)
					)

			# Handle everything else (structures)
			else:

				# HACK TODO
				arguments_list.append(None)

		# Return args as tuple and kw as dict
		return tuple(arguments_list), {} # TODO kw not yet handled


	def __unpack_datatype_dict__(self, datatype_dict):

		# Handle the 'easy' stuff ...
		if datatype_dict['t'] in FUNDAMENTAL_C_DATATYPES:

			# Return type class or type pointer
			if datatype_dict['p']:
				return ctypes.POINTER(getattr(ctypes, datatype_dict['t']))
			else:
				return getattr(ctypes, datatype_dict['t'])

		# And now the hard stuff ...
		else:

			# Push traceback to log
			self.log.out('[_server_] ... unhandled datatype: %s ...' % datatype_dict['t'])

			# HACK TODO
			return ctypes.c_int


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	# Parse arguments comming from unix side
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--id', type = str, nargs = 1
		)
	parser.add_argument(
		'--port_socket_ctypes', type = int, nargs = 1
		)
	parser.add_argument(
		'--port_socket_log_main', type = int, nargs = 1
		)
	parser.add_argument(
		'--log_level', type = int, nargs = 1
		)
	args = parser.parse_args()

	# Generate parameter dict
	parameter = {
		'id': args.id[0],
		'platform': 'WINE',
		'stdout': False,
		'stderr': False,
		'logwrite': True,
		'remote_log': True,
		'log_level': args.log_level[0],
		'log_server': False,
		'port_socket_ctypes': args.port_socket_ctypes[0],
		'port_socket_log_main': args.port_socket_log_main[0]
		}

	# Fire up wine server session with parsed parameters
	session = wine_server_class(parameter['id'], parameter)
