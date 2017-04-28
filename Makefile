init:
    pip install 'flickr_api~=0.5' --target ./libs
    pip install 'argparse~=1.4.0' --target ./libs

test:
    py.test tests
