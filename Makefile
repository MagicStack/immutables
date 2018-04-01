.PHONY: rtest build test


build:
	python setup.py build_ext --inplace

test:
	python setup.py test -v

rtest:
	env PYTHONPATH=. \
		~/dev/venvs/36-debug/bin/python -m test.regrtest -R3:3 --testdir tests/
