# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_bubblesort.py: Test bidirectional memory sync for pointers

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

import pytest

from sys import platform
if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
	from zugbruecke import ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# void bubblesort(float *, int n)
		self.__bubblesort__ = self.__dll__.bubblesort
		self.__bubblesort__.memsync = [ # Regular ctypes on Windows should ignore this statement
			{
				'p': [0], # "path" to argument containing the pointer
				'l': [1], # "path" to argument containing the length
				'_t': ctypes.c_float # type of argument (optional, default char/byte): sizeof(type) * length == bytes
				}
			]
		self.__bubblesort__.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int)


	def bubblesort(self, values):

		ctypes_float_values = ((ctypes.c_float)*len(values))(*values)
		ctypes_float_pointer_firstelement = ctypes.cast(
			ctypes.pointer(ctypes_float_values), ctypes.POINTER(ctypes.c_float)
			)
		self.__bubblesort__(ctypes_float_pointer_firstelement, len(values))
		values[:] = ctypes_float_values[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_bubblesort():

	sample = sample_class()

	test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
	sample.bubblesort(test_vector)
	test_vector = [round(element, 2) for element in test_vector]
	result_vector = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]
	vector_diff = sum([abs(test_vector[index] - result_vector[index]) for index in range(len(result_vector))])

	assert pytest.approx(0.0, 0.0000001) == vector_diff