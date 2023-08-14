import os
import platform
import setuptools


system = platform.uname().system
CFLAGS = ['-O2']

if system == 'AIX':
    CFLAGS.extend(['-qlanglvl=stdc99', '-qchars'])
elif system == 'SUNOS':
    CFLAGS.extend(['-xc99'])  # -xchar=s is the default
elif system != 'Windows':
    CFLAGS.extend(['-std=c99', '-fsigned-char', '-Wall',
                   '-Wsign-compare', '-Wconversion'])


with open(os.path.join(
        os.path.dirname(__file__), 'immutables', '_version.py')) as f:
    for line in f:
        if line.startswith('__version__ ='):
            _, _, version = line.partition('=')
            VERSION = version.strip(" \n'\"")
            break
    else:
        raise RuntimeError(
            'unable to read the version from immutables/_version.py')


if platform.python_implementation() == 'CPython':
    if os.environ.get("DEBUG_IMMUTABLES") == '1':
        define_macros = []
        undef_macros = ['NDEBUG']
    else:
        define_macros = [('NDEBUG', '1')]
        undef_macros = []

    ext_modules = [
        setuptools.Extension(
            "immutables._map",
            ["immutables/_map.c"],
            extra_compile_args=CFLAGS,
            define_macros=define_macros,
            undef_macros=undef_macros)
    ]
else:
    ext_modules = []


setuptools.setup(
    version=VERSION,
    ext_modules=ext_modules,
)
