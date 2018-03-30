import platform
import setuptools


VERSION = '0.1'

CFLAGS = ['-O2']

if platform.uname().system != 'Windows':
    CFLAGS.extend(['-fsigned-char', '-Wall', '-Wsign-compare', '-Wconversion'])


setuptools.setup(
    name='immutables',
    version=VERSION,
    description='Immutable Collections',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    platforms=['POSIX'],
    author='MagicStack Inc',
    author_email='hello@magic.io',
    url='https://github.com/MagicStack/immutables',
    license='Apache License, Version 2.0',
    packages=['immutables'],
    provides=['immutables'],
    include_package_data=True,
    ext_modules=[
        setuptools.Extension(
            "immutables._map",
            ["immutables/_map.c"],
            extra_compile_args=CFLAGS)
    ],
    test_suite='tests.suite',
)
