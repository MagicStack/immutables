import os.path
import platform
import setuptools


CFLAGS = ['-O2']
if platform.uname().system != 'Windows':
    CFLAGS.extend(['-std=c99', '-fsigned-char', '-Wall',
                   '-Wsign-compare', '-Wconversion'])


with open(os.path.join(
        os.path.dirname(__file__), 'immutables', '__init__.py')) as f:
    for line in f:
        if line.startswith('__version__ ='):
            _, _, version = line.partition('=')
            VERSION = version.strip(" \n'\"")
            break
    else:
        raise RuntimeError(
            'unable to read the version from immutables/__init__.py')


if platform.python_implementation() == 'CPython':
    ext_modules = [
        setuptools.Extension(
            "immutables._map",
            ["immutables/_map.c"],
            extra_compile_args=CFLAGS)
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
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    author='MagicStack Inc',
    author_email='hello@magic.io',
    url='https://github.com/MagicStack/immutables',
    license='Apache License, Version 2.0',
    packages=['immutables'],
    provides=['immutables'],
    include_package_data=True,
    ext_modules=ext_modules,
    test_suite='tests.suite',
)
