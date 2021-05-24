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

### Trigger Service

First, to import and initiate the library


```python
import etap.trigger as trigger

trigger.init(db_file=memory_file_location, init_db=True)
# By default, the database is stored in memory
```

To add a trigger secret key

```python
trigger.add_new_secret(trigger_id, secret_key, formatter)
```
where 
- `trigger_id` is an identifier that uniquely identifies the (trigger, user) pair
- `secret_key` is a 128-bit token
- `formatter` is the input format (for simplicity, we will assume that the client specifies the input format, see [Client Usage](#Client) for more details)



Assume that a trigger service API (with ID `trigger_id`) needs to send the variable `trigger_data` and `trigger_payload` to TAP,  you can encrypt the data and payload using the `trigger.encode` function.

```python
trigger_data = ...

trigger_payload = ...

circuit_id, X, ct = trigger.encode(trigger_id, trigger_data, trigger_payload)
```


### Action Service

First, to import and initiate the library

```python
import etap.action as action 

action.init(db_file=memory_file_location, init_db=True, accept_window=30)
# By default, the database is stored in memory
# accept_window is the number of seconds allowed for stale messages
```

To add a action secret key

```python
action.add_new_secret(action_id, secret_key, formatter)
```
where 
- `action_id` is an identifier that uniquely identifies the (action, user) pair
- `secret_key` is a 128-bit token
- `formatter` is the output format (for simplicity, we will assume that the client specifies the output format, see [Client](../client/) for more details)



Assume that a action service API (with ID `action_id`) receives the tuple `(j, Y, ct, d)` from TAP and wants to decode the action data and payload as `action_data` and `action_payload`,  you can use the `action.decode` function.

```python
y, payload = action.decode(action_id, [j, Y, ct, d])
```