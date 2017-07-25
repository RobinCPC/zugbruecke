:github_url:

.. _examples:

.. index::
	pair: cdll; example
	pair: windll; example
	pair: oledll; example
	pair: memsync; example
	single: demo_dll

Examples
========

A lot of code, which was written with ``cdll``, ``windll`` or ``oledll``
in mind and which runs under *Windows*, should run just fine with *zugbruecke*
on Unix.

.. code:: python

	from zugbruecke import windll, c_float

	simple_demo_routine = windll.LoadLibrary('demo_dll.dll').simple_demo_routine
	simple_demo_routine.argtypes = [c_float, c_float]
	simple_demo_routine.restype = c_float
	return_value = simple_demo_routine(20.0, 1.07)
	print('Got "%f".' % return_value)

It will print ``Got "1.308412".`` assuming that the corresponding routine in the DLL
looks somewhat like this:

.. code:: c

	float __stdcall __declspec(dllimport) simple_demo_routine(float param_a, float param_b)
	{ return param_a - (param_a / param_b); }

Because of the drop-in replacement design of zugbruecke, it is possible to write
Python code which works under both Unices and Windows.

.. code:: python

	from sys import platform
	if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
		from zugbruecke import cdll
	elif platform.startswith('win'):
		from ctypes import cdll
	else:
		# Handle unsupported platforms

For more examples check the `examples directory`_ of this project.
For the full DLL source code check the `demo_dll directory`_ of this project.

.. _examples directory: https://github.com/pleiszenburg/zugbruecke/tree/master/examples
.. _demo_dll directory: https://github.com/pleiszenburg/zugbruecke/tree/master/demo_dll

Please also consult the `documentation of ctypes`_.

.. _documentation of ctypes: https://docs.python.org/3/library/ctypes.html