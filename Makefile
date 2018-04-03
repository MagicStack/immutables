.PHONY: rtest build test clean


build:
	python setup.py build_ext --inplace

test:
	python setup.py test -v

rtest:
	~/dev/venvs/36-debug/bin/python setup.py build_ext --inplace

	env PYTHONPATH=. \
		~/dev/venvs/36-debug/bin/python -m test.regrtest -R3:3 --testdir tests/

clean:
	find . -name '*.pyc' | xargs rm
	find . -name '*.so' | xargs rm
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./*.egg-info
