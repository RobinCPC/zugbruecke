# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/routine_server.py: Classes for managing routines in DLLs

	Required to run on platform / side: [WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import ctypes
from pprint import pformat as pf
import traceback

from .arg_contents import arg_contents_class
from .arg_definition import arg_definition_class
from .arg_memory import arg_memory_class
from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_server_class(
	arg_contents_class,
	arg_definition_class,
	arg_memory_class
	):


	def __init__(self, parent_dll, routine_name, routine_handler):

		# Store handle on parent dll
		self.dll = parent_dll

		# Store pointer to zugbruecke session
		self.session = self.dll.session

		# Get handle on log
		self.log = self.dll.log

		# Store my own name
		self.name = routine_name

		# Set routine handler
		self.handler = routine_handler


	def call_routine(self, arg_message_list, arg_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-server] Trying call routine "%s" ...' % self.name)

		# Unpack passed arguments, handle pointers and structs ...
		args_list = self.server_unpack_arg_list(self.argtypes_d, arg_message_list)

		# Unpack pointer data
		memory_transport_handle = self.server_unpack_memory_list(args_list, arg_memory_list, self.memsync_d)

		# Default return value
		return_value = None

		# This is risky
		try:

			# Call into dll
			return_value = self.handler(*tuple(args_list))

			# Log status
			self.log.out('[routine-server] ... done.')

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

		# Pack memory for return
		return_memory_list = self.server_pack_memory_list(memory_transport_handle)

		try:

			# Pack return package and return it
			return {
				'args': self.server_pack_return_list(self.argtypes_d, args_list),
				'return_value': return_value, # TODO allow & handle pointers
				'memory': return_memory_list
				}

		except:

			# Push traceback to log
			self.log.err(traceback.format_exc())


	def register_argtype_and_restype(self, argtypes_d, restype_d, memsync_d):

		# Log status
		self.log.out('[routine-server] Set argument and return value types for "%s" ...' % self.name)

		# Store memory sync instructions
		self.memsync_d = memsync_d

		# Store argtype definition dict
		self.argtypes_d = argtypes_d

		# Parse and apply argtype definition dict to actual ctypes routine
		self.handler.argtypes = self.unpack_definition_argtypes(argtypes_d)

		# Store return value definition dict
		self.restype_d = restype_d

		# Parse and apply restype definition dict to actual ctypes routine
		self.handler.restype = self.unpack_definition_returntype(restype_d)

		# Log status
		self.log.out('[routine-server] ... memsync: %s ...' % pf(self.memsync_d))
		self.log.out('[routine-server] ... argtypes: %s ...' % pf(self.handler.argtypes))
		self.log.out('[routine-server] ... restype: %s ...' % pf(self.handler.restype))

		# Log status
		self.log.out('[routine-server] ... done.')

		return True # Success
