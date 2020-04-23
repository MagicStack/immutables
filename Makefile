.PHONY: rtest build test clean all


PYTHON ?= python
ROOT = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))


all: build

build:
	$(PYTHON) setup.py build_ext --inplace

debug:
	DEBUG_IMMUTABLES=1 $(PYTHON) setup.py build_ext --inplace

test:
	$(PYTHON) setup.py test -v

rtest:
	~/dev/venvs/36-debug/bin/python setup.py build_ext --inplace

	env PYTHONPATH=. \
		~/dev/venvs/36-debug/bin/python -m test.regrtest -R3:3 --testdir tests/

clean:
	find . -name '*.pyc' | xargs rm -f
	find . -name '*.so' | xargs rm -f
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./*.egg-info

testinstalled:
	cd /tmp && $(PYTHON) $(ROOT)/tests/__init__.py
