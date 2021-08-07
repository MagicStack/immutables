import os
import platform
import setuptools


# Minimal dependencies required to test immutables.
TEST_DEPENDENCIES = [
    # pycodestyle is a dependency of flake8, but it must be frozen because
    # their combination breaks too often
    # (example breakage: https://gitlab.com/pycqa/flake8/issues/427)
    'flake8~=3.8.4',
    'pycodestyle~=2.6.0',
    'mypy>=0.910',
    'pytest~=6.2.4',
]

EXTRA_DEPENDENCIES = {
    'test': TEST_DEPENDENCIES,
}

CFLAGS = ['-O2']
if platform.uname().system != 'Windows':
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


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()


setuptools.setup(
    name='immutables',
    version=VERSION,
    description='Immutable Collections',
    long_description=readme,
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    author='MagicStack Inc',
    author_email='hello@magic.io',
    url='https://github.com/MagicStack/immutables',
    license='Apache License, Version 2.0',
    packages=['immutables'],
    package_data={"immutables": ["py.typed", "*.pyi"]},
    provides=['immutables'],
    include_package_data=True,
    ext_modules=ext_modules,
    install_requires=['typing-extensions>=3.7.4.3;python_version<"3.8"'],
    extras_require=EXTRA_DEPENDENCIES,
)
