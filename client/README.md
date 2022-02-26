# eTAP-compatible client

This directory contains an example implementation of a eTAP-compatible client.


## Environment Setup

First, install the following prerequisites:

1. Python 3.8 or higher
2. `aiohttp`, `requests`,`cryptography`, and `flask` Python packages

Next, install the [EMP-toolkit](https://github.com/emp-toolkit) using the provided script [`scripts/install_emp-tool.sh`](../scripts/install_pybind11.sh). **Note**: we are using an older version of the EMP-toolkit and may be not compatible with the more recent versions.


## Build Instruction

First, build the binaries inside the [emp_src](../emp_src/) directory.

```
cd emp_src/
cmake .
make
```

Next, make sure that the `etaplib` Python Module is correctly built and is in the Python import path. Please refer to the `README` in the [etaplib](../etaplib/) directory for detailed instructions.

## Usage

```
EMP_CLIENT_BINARY="../emp_src/bin/client" python3 ./client.py rule_desc_file trigger_data_file
```


### Rule description file format

```
// First declare the input variables (starting with 'x') and their types.
// For string variables, their lengths are also required
x0 int 
x1 str 512

// Then declare any user constant values (starting with 'c') with their types and values
c0 str test_user@sample_website.com
c1 bool 0
c2 int 42

// Next, express the intermediate variables (starting with 'i') and how to compute them. 
// For string operations, please also specify the full path to the corresponding DFA files.
i0 contain x1 /path/to/dfa/files
i1 + x0 c2

// Finally, specify which variables are output variables.
// Denote the predicate with 'p', while other output variables (representing action data) should start with 'y'
p i0
y0 i1
y1 c0
```

The the operations implemented in this prototype are listed below (please refer to [`emp_src/test/func_reader.cpp`](emp_src/test/func_reader.cpp) for more details)

```
not [arg1]
and/or/>/</+/-/*///eq/start_with [arg1] [arg2]
end_with/contain/split [arg1] [dfa_file_path]
remove [arg1] [dfa_file_path] [reverse_dfa_file_path]
lookup [arg1] [key_len] [val_len] [key1] [val1] [key2] [val2] ...
```

#### How to generate DFA files

We provide a Java helper file `ExampleRuleDFA.java` that shows how to generate the DFA files for rules listed in Fig 9.


### Trigger data file format

A trigger data file is needed for the client to manually trigger the rule with the provided data. It should contain a JSON list of values for all input variables
```
[84, "test input data"]
```

