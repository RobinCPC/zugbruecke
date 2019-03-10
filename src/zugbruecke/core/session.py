# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/session.py: A user-facing ctypes-drop-in-replacement session

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
# IMPORT: Original ctypes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import ctypes as __ctypes__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Unix ctypes members required by wrapper, which will exported as they are
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import (
	_FUNCFLAG_CDECL,
	DEFAULT_MODE,
	LibraryLoader
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Unix ctypes members, which will be modified
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import CDLL as __ctypes_CDLL_class__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core and missing ctypes flags
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .session_client import session_client_class as __session_client_class__
from .const import _FUNCFLAG_STDCALL # EXPORT


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION CTYPES-DROP-IN-REPLACEMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_class:


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# static components
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	DEFAULT_MODE = DEFAULT_MODE
	LibraryLoader = LibraryLoader
	_FUNCFLAG_CDECL = _FUNCFLAG_CDECL
	_FUNCFLAG_STDCALL = _FUNCFLAG_STDCALL


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# constructor
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def __init__(self, parameter = None, force = False):

		if parameter is None:
			parameter = {}
		elif not isinstance(parameter, dict):
			raise TypeError('parameter "parameter" must be a dict')

		if not isinstance(force, bool):
			raise TypeError('parameter "force" must be a bool')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# zugbruecke session client and session interface
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

		# Start new zugbruecke session
		self._zb_current_session = __session_client_class__(parameter = parameter, force = force)

		# Offer access to session internals
		self._zb_set_parameter = self._zb_current_session.set_parameter
		self._zb_terminate = self._zb_current_session.terminate


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows - accessed via server
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

		self.FormatError = self._zb_current_session.ctypes_FormatError

		self.get_last_error = self._zb_current_session.ctypes_get_last_error

		self.GetLastError = self._zb_current_session.ctypes_GetLastError

		self.set_last_error = self._zb_current_session.ctypes_set_last_error

		self.WinError = self._zb_current_session.ctypes_WinError


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CFUNCTYPE & WINFUNCTYPE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

		# CFUNCTYPE and WINFUNCTYPE function pointer factories
		self.CFUNCTYPE = self._zb_current_session.ctypes_CFUNCTYPE
		self.WINFUNCTYPE = self._zb_current_session.ctypes_WINFUNCTYPE

		# Used as cache by CFUNCTYPE and WINFUNCTYPE
		self._c_functype_cache = self._zb_current_session.data.cache_dict['func_type'][_FUNCFLAG_CDECL]
		self._win_functype_cache = self._zb_current_session.data.cache_dict['func_type'][_FUNCFLAG_STDCALL]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Wine-related stuff
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

		self._zb_path_unix_to_wine = self._zb_current_session.path_unix_to_wine
		self._zb_path_wine_to_unix = self._zb_current_session.path_wine_to_unix


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Set up and expose dll library loader objects
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

		# Set up and expose dll library loader objects
		self.cdll = LibraryLoader(self.CDLL)
		self.windll = LibraryLoader(self.WinDLL)
		self.oledll = LibraryLoader(self.OleDLL)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Allow readonly access to session states
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@property
	def _zb_id(self):
		return self._zb_current_session.id

	@property
	def _zb_up(self):
		return self._zb_current_session.up


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@staticmethod
	def DllCanUnloadNow(): # EXPORT
		pass # TODO stub - required for COM

	@staticmethod
	def DllGetClassObject(rclsid, riid, ppv): # EXPORT
		pass # TODO stub - required for COM

	class HRESULT: # EXPORT
		pass # TODO stub - special form of c_long, will require changes to argument parser

	@staticmethod
	def _check_HRESULT(result): # EXPORT
		pass # TODO stub - method for HRESULT, checks error bit, raises error if true. Needs reimplementation.


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Wrapper around DLL / shared object interface classes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	# Wrapper for CDLL class
	def CDLL(
		self,
		name, mode = DEFAULT_MODE, handle = None,
		use_errno = False,
		use_last_error = False
		):

		# If there is a handle to a zugbruecke session, return session
		if handle is not None:

			# Handle zugbruecke handle
			if type(handle).__name__ == 'dll_client_class':

				# Return it as-is TODO what about a new name?
				return handle

			# Handle ctypes handle
			else:

				# Return ctypes DLL class instance, let it handle the handle as it would
				return __ctypes_CDLL_class__(name, mode, handle, use_errno, use_last_error)

		# If no handle was passed, it's a new library
		else:

			# Let's try the Wine side first
			try:

				# Return a handle on dll_client object
				return self._zb_current_session.load_library(
					dll_name = name, dll_type = 'cdll', dll_param = {
						'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
						}
					)

			# Well, it might be a Unix library after all
			except:

				# If Unix library, return CDLL class instance
				return __ctypes_CDLL_class__(name, mode, handle, use_errno, use_last_error)


	# Wrapper for WinDLL class
	def WinDLL(
		self,
		name, mode = DEFAULT_MODE, handle = None,
		use_errno = False,
		use_last_error = False
		):

		return self._zb_current_session.load_library(
			dll_name = name, dll_type = 'windll', dll_param = {
				'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
				}
			)


	# Wrapper for OleDLL class
	def OleDLL(
		self,
		name, mode = DEFAULT_MODE, handle = None,
		use_errno = False,
		use_last_error = False
		):

		return self._zb_current_session.load_library(
			dll_name = name, dll_type = 'oledll', dll_param = {
				'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
				}
			)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# more static components from ctypes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

_ctypes_veryprivate_ = [
	'__version__'
	]

__ctypes_private__ = [
	'_CFuncPtr',
	'_FUNCFLAG_PYTHONAPI',
	'_FUNCFLAG_USE_ERRNO',
	'_FUNCFLAG_USE_LASTERROR',
	'_Pointer',
	'_SimpleCData',
	'_calcsize',
	'_cast',
	'_cast_addr',
	'_check_size',
	'_ctypes_version',
	'_dlopen', # behaviour depends on platform
	'_endian',
	'_memmove_addr',
	'_memset_addr',
	'_pointer_type_cache',
	'_reset_cache',
	'_string_at',
	'_string_at_addr',
	'_wstring_at',
	'_wstring_at_addr'
	]

__ctypes_public__ = [
	'ARRAY', # Python 3.6: Deprecated XXX
	'ArgumentError',
	'Array',
	'BigEndianStructure',
	'LittleEndianStructure',
	'POINTER',
	'PYFUNCTYPE',
	'PyDLL',
	'RTLD_GLOBAL',
	'RTLD_LOCAL',
	'SetPointerType', # Python 3.6: Deprecated XXX
	'Structure',
	'Union',
	'addressof',
	'alignment',
	'byref',
	'c_bool',
	'c_buffer',
	'c_byte',
	'c_char',
	'c_char_p',
	'c_double',
	'c_float',
	'c_int',
	'c_int16',
	'c_int32',
	'c_int64',
	'c_int8',
	'c_long',
	'c_longdouble',
	'c_longlong',
	'c_short',
	'c_size_t',
	'c_ssize_t',
	'c_ubyte',
	'c_uint',
	'c_uint16',
	'c_uint32',
	'c_uint64',
	'c_uint8',
	'c_ulong',
	'c_ulonglong',
	'c_ushort',
	'c_void_p',
	'c_voidp',
	'c_wchar',
	'c_wchar_p',
	'cast',
	'create_string_buffer',
	'create_unicode_buffer',
	'get_errno',
	'memmove',
	'memset',
	'pointer',
	'py_object',
	'pydll',
	'pythonapi',
	'resize',
	'set_errno',
	'sizeof',
	'string_at',
	'wstring_at'
	]

for __ctypes_item__ in _ctypes_veryprivate_ + __ctypes_private__ + __ctypes_public__:
	__ctypes_attr__ = getattr(__ctypes__, __ctypes_item__)
	if hasattr(__ctypes_attr__, '__call__'):
		__ctypes_attr__ = staticmethod(__ctypes_attr__)
	setattr(session_class, __ctypes_item__, __ctypes_attr__)