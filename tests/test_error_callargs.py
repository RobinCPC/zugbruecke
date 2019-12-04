# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_error_callargs.py: Test error handling when malformed arguments are passed

	Required to run on platform / side: [UNIX, WINE]

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
# C
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

HEADER = """
{{ PREFIX }} int16_t {{ SUFFIX }} square_int(
	int16_t a
	);

{{ PREFIX }} int16_t {{ SUFFIX }} add_ints(
	int16_t a,
	int16_t b
	);

{{ PREFIX }} int16_t {{ SUFFIX }} mul_ints(
	int16_t a,
	int16_t b
	);

{{ PREFIX }} float {{ SUFFIX }} add_floats(
	float a,
	float b
	);

{{ PREFIX }} int16_t {{ SUFFIX }} subtract_ints(
	int16_t a,
	int16_t b
	);

{{ PREFIX }} int16_t {{ SUFFIX }} pow_ints(
	int16_t a,
	int16_t b
	);
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} square_int(
	int16_t a
	)
{
	return a * a;
}

{{ PREFIX }} int16_t {{ SUFFIX }} add_ints(
	int16_t a,
	int16_t b
	)
{
	return a + b;
}

{{ PREFIX }} int16_t {{ SUFFIX }} mul_ints(
	int16_t a,
	int16_t b
	)
{
	return a * b;
}

{{ PREFIX }} float {{ SUFFIX }} add_floats(
	float a,
	float b
	)
{
	return a + b;
}

{{ PREFIX }} int16_t {{ SUFFIX }} subtract_ints(
	int16_t a,
	int16_t b
	)
{
	return a - b;
}

{{ PREFIX }} int16_t {{ SUFFIX }} pow_ints(
	int16_t a,
	int16_t b
	)
{
	return pow(a, b);
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_unconfigured_too_many_args(arch, conv, ctypes, dll_handle):

	square_int = dll_handle.square_int

	if arch == 'win64' or conv == 'cdll':
		a = square_int(1, 2, 3) # ctypes will ignore this case
	else:
		with pytest.raises(ValueError):
			a = square_int(1, 2, 3)

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_unconfigured_too_few_args(arch, conv, ctypes, dll_handle):

	mul_ints = dll_handle.mul_ints

	if arch == 'win64' or conv == 'cdll':
		a = mul_ints(7) # ctypes will ignore this case
	else:
		with pytest.raises(ValueError):
			a = mul_ints(7)

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_unconfigured_right_number_of_args(arch, conv, ctypes, dll_handle):

	add_ints = dll_handle.add_ints

	assert 7 == add_ints(3, 4)

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_unconfigured_right_number_of_args_nondefault_float(arch, conv, ctypes, dll_handle):

	add_floats = dll_handle.add_floats

	with pytest.raises(ctypes.ArgumentError):
		a = add_floats(1.2, 3.6)

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_configured_too_few_args(arch, conv, ctypes, dll_handle):

	subtract_ints = dll_handle.subtract_ints
	subtract_ints.argtypes = (ctypes.c_int16, ctypes.c_int16)
	subtract_ints.restype = ctypes.c_int16

	with pytest.raises(TypeError):
		a = subtract_ints(7)

@pytest.mark.parametrize('arch,conv,ctypes,dll_handle', get_context(__file__))
def test_error_callargs_configured_too_many_args(arch, conv, ctypes, dll_handle):

	pow_ints = dll_handle.pow_ints
	pow_ints.argtypes = (ctypes.c_int16, ctypes.c_int16)
	pow_ints.restype = ctypes.c_int16

	if conv == 'cdll':
		a = pow_ints(7, 2, 99) # ctypes will ignore this case
	else:
		with pytest.raises(TypeError):
			a = pow_ints(7, 2, 99)