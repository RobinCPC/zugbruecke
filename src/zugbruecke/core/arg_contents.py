# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/arg_contents.py: (Un-) packing of argument contents

	Required to run on platform / side: [UNIX, WINE]

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

from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class arg_contents_class():


	def client_pack_arg_list(self, argtypes_d_sub, args):

		return self.__pack_arg_list__(argtypes_d_sub, args)


	def client_unpack_return_list(self, argtypes_d, old_arguments_list, new_arguments_list):
		"""
		TODO Optimize for speed!
		"""

		# Step through arguments
		for arg_index, old_arg in enumerate(old_arguments_list):

			# Fetch definition of current argument
			argtype_d = argtypes_d[arg_index]

			# Handle fundamental types
			if argtype_d['g'] == GROUP_FUNDAMENTAL:

				# Start process with plain old argument
				old_arg_ref = old_arg

				# Step through flags
				for flag in argtype_d['f']:

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						if hasattr(old_arg_ref, 'contents'):
							old_arg_ref = old_arg_ref.contents
						else:
							old_arg_ref = old_arg_ref

					# Handle arrays
					elif flag > 0:

						old_arg_ref = old_arg_ref # TODO ???

					# Handle unknown flags
					else:

						raise # TODO

				if hasattr(old_arg_ref, 'value'):
					old_arg_ref.value = new_arguments_list[arg_index]
				else:
					old_arg_ref = new_arguments_list[arg_index]

			# Handle everything else (structures and "the other stuff")
			else:

				# HACK TODO
				pass


	def server_pack_return_list(self, argtypes_d, args):
		"""
		TODO: Optimize for speed!
		"""

		# Start argument list as a list
		args_package_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			argtype_d = argtypes_d[arg_index]

			arg_value = arg # Set up arg for iterative unpacking
			for flag in argtype_d['f']: # step through flags

				# Handle pointers
				if flag == FLAG_POINTER:

					# There are two ways of getting the actual value
					if hasattr(arg_value, 'value'):
						arg_value = arg_value.value
					elif hasattr(arg_value, 'contents'):
						arg_value = arg_value.contents
					else:
						pass
						# self.log.err(pf(arg_value))
						# raise # TODO

				# Handle arrays
				elif flag > 0:

					arg_value = arg_value[:]

				# Handle unknown flags
				else:

					self.log.err('ERROR in __pack_return__, flag %d' % flag)
					raise # TODO

			self.log.err('== server_pack_return_list ==')
			self.log.err(pf(arg_value))

			# Handle fundamental types by value
			if argtype_d['g'] == GROUP_FUNDAMENTAL:

				if hasattr(arg_value, 'value'):
					arg_value = arg_value.value
				args_package_list.append(arg_value)

				# # If by reference ...
				# if argtype_d['p']:
				# 	# Append value from ctypes datatype (because most of their Python equivalents are immutable)
				# 	args_package_list.append(arg.value)
				# # If by value ...
				# else:
				# 	# Nothing to do ...
				# 	args_package_list.append(None)

			# Handle everything else (structures etc)
			else:

				# HACK TODO
				args_package_list.append(None)

		return args_package_list


	def server_unpack_arg_list(self, argtypes_d, args_package_list):
		"""
		TODO Optimize for speed!
		"""

		# Start argument list as a list (will become a tuple)
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args_package_list):

			arguments_list.append(self.__unpack_item__(arg[1], argtypes_d[arg_index]))

		# Return args as list, will be converted into tuple on call
		return arguments_list


	def __pack_arg_list__(self, argtypes_d_sub, args):

		# Shortcut for speed
		args_package_list = []

		# Step through arguments
		for arg_index, argtype_d in enumerate(argtypes_d_sub):

			# Fetch current argument by index from tuple or by name from struct/kw
			if type(args) is list or type(args) is tuple:
				arg = args[arg_index]
			else:
				arg = getattr(args, argtype_d['n'])

			# TODO:
			# append tuple to list "args_package_list"
			# tuple contains: (argtype_d['n'], argument content / value)
			#  pointer: arg.value or arg.contents.value
			#  (value: Append value from ctypes datatype, because most of their Python equivalents are immutable)
			#  (contents.value: Append value from ctypes datatype pointer ...)
			#  by value: just "arg"

			try:

				arg_value = arg # Set up arg for iterative unpacking
				for flag in argtype_d['f']: # step through flags

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						if hasattr(arg_value, 'value'):
							arg_value = arg_value.value
						elif hasattr(arg_value, 'contents'):
							arg_value = arg_value.contents
						else:
							raise # TODO

					# Handle arrays
					elif flag > 0:

						arg_value = arg_value[:]

					# Handle unknown flags
					else:

						raise # TODO
			except:

				self.log.err(pf(arg_value))

			self.log.err('== __pack_arg_list__ ==')
			self.log.err(pf(arg_value))

			# Handle fundamental types
			if argtype_d['g'] == GROUP_FUNDAMENTAL:

				# Append argument to list ...
				args_package_list.append((argtype_d['n'], arg_value))

			# Handle structs
			elif argtype_d['g'] == GROUP_STRUCT:

				# Reclusively call this routine for packing structs
				args_package_list.append((argtype_d['n'], self.__pack_arg_list__(
					argtype_d['_fields_'], arg
					)))

			# Handle everything else ... likely pointers handled by memsync
			else:

				# Just return None - will (hopefully) be overwritten by memsync
				args_package_list.append((None, None))

		# Return parameter message list - MUST WORK WITH PICKLE
		return args_package_list


	def __pack_item__(self):

		pass


	def __pack_item_fundamental__(self):

		pass


	def __pack_item_struct__(self):

		pass


	def __unpack_item__(self, arg_raw, arg_def_dict):

		# Handle fundamental types
		if arg_def_dict['g'] == GROUP_FUNDAMENTAL:

			return self.__unpack_item_fundamental__(arg_raw, arg_def_dict)

		# Handle structs
		elif arg_def_dict['g'] == GROUP_STRUCT:

			return self.__unpack_item_struct__(arg_raw, arg_def_dict)

		# Handle voids (likely mensync stuff)
		elif arg_def_dict['g'] == GROUP_VOID:

			# Return a placeholder
			return 0

		# Handle everything else ...
		else:

			# HACK TODO
			self.log.err('__unpack_item__ NEITHER STRUCT NOR FUNDAMENTAL?')
			self.log.err(str(arg_def_dict['g']))
			return None


	def __unpack_item_fundamental__(self, arg_rebuilt, arg_def_dict):

		try:

			self.log.err(pf(arg_def_dict))
			self.log.err(pf(arg_rebuilt))

			# Handle scalars, whether pointer or not
			if arg_def_dict['s']:
				arg_rebuilt = getattr(ctypes, arg_def_dict['t'])(arg_rebuilt)

			# Step through flags in reverse order
			for flag in reversed(arg_def_dict['f']):

				if flag == FLAG_POINTER:

					arg_rebuilt = ctypes.pointer(arg_rebuilt)

				elif flag > 0:

					# TODO does not really handle arrays of arrays (yet)
					arg_rebuilt = (flag * getattr(ctypes, arg_def_dict['t']))(*arg_rebuilt)

				else:

					raise

			return arg_rebuilt

		except:

			self.log.err('ERROR in __unpack_item_fundamental__, fundamental datatype path')
			self.log.err(traceback.format_exc())

			return None # Good idea ...?


	def __unpack_item_struct__(self, args_list, struct_def_dict):

		# Generate new instance of struct datatype
		struct_inst = self.struct_type_dict[struct_def_dict['t']]()

		# Fetch fields for speed
		struct_fields = struct_def_dict['_fields_']

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			setattr(
				struct_inst, # struct instance to be modified
				arg[0], # parameter name (from tuple)
				self.__unpack_item__(arg[1], struct_fields[arg_index]) # parameter value
				)

		return struct_inst
