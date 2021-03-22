# `etaplib` Python Module

This directory contains the `etaplib` Python module. It allows developers of trigger and action services to  upgrade their existing Flask API routes to be compatible with eTAP.

## Build Instruction

1. Install [pybind11](https://pybind11.readthedocs.io/en/stable/). We provide a helper script in [`scripts/install_pybind11.sh`](../scripts/install_pybind11.sh).

2. Install the [EMP-toolkit](https://github.com/emp-toolkit) using the provided script [`scripts/install_emp-tool.sh`](../scripts/install_pybind11.sh). **Note**: we are using an old version of the EMP-toolkit and may be not compatible with the more recent versions.

3. Build the required C++ bindings:
```
cd etaplib/emp_utils
cmake .
make
```

4. Make sure that the generated `emp_utils.cpython-****.so` file is in the current Python path.  

## Usage

## TODO: add usages