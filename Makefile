.PHONY: init test

init:
	pip install 'flickr_api~=0.5' 'argparse~=1.4.0' 'mock~=2.0.0' --target ./libs

test:
	python -m unittest discover -s test -p '*_test.py'
