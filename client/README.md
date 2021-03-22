# eTAP-compatible client

This directory contains an example implementation of a eTAP-compatible client.


## Environment Setup

First, install the following prerequisites:

1. Python 3.8 or higher
2. `aiohttp`, `requests`,`cryptography`, and `flask` Python packages

Next, install the [EMP-toolkit](https://github.com/emp-toolkit) using the provided script [`script/install_emp-tool.sh`](../scripts/install_pybind11.sh). **Note**: we are using an old version of the EMP-toolkit and may be not compatible with the more recent versions.


## Build Instruction

First, build the binaries inside the [emp_src](../emp_src/) directory.

```
cd emp_src/
cmake .
make
```

Next, make sure that the `etaplib` Python Module is correctly built and is in the Python import path. Please refer to the `README` in the [etaplib](../etaplib/) directory for detailed instructions.

## TODO: add instruction to create rule description file