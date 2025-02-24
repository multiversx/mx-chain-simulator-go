## Chain Simulator Examples

In these examples, we are mostly going to use the [Python SDK](https://github.com/multiversx/mx-sdk-py).

Before starting, make sure you have Python installed on your machine. We recommend using `Python 3.11` or greater, but the sdk should work with any version greater than `3.8`.

For managing the dependencies, we recommend using a virtual environment, so make sure you have `virtualenv` installed, as well.

### Creating the virtual environment

Make sure the current working directory is the `examples` directory.

To create the virtual environment, run the following commands:
```sh
python3 -m venv ./venv
source ./venv/bin/activate
```

To install the dependencies, run the following command:
```sh
pip install -r ./requirements.txt --upgrade
```

After these steps, make sure you select the correct interpreter. It should be located in `./venv/bin/python`.
