# Overview of EMP-toolkit implementation

Once the EMP-toolkit library is imported, the program will automatically include two global variables that are responsible for running the MPC:

- `ProtocolExecution * prot_exec`: It encodes bits into labels (which are represented though the `block` type) and decodes labels into bits. It may also include an `IO` variable, which is used to transfer labels and initiate oblivious transfer when necessary.
- `CircuitExecution * circ_exec`: It contains functions that take the input labels and produce the output label for each type of boolean gate. Depends on the role of the program, the purpose of the function will vary:
  - If the program is a **generator** (ALICE), it will generate the table for this gate and send the table through an `IO`. In the case, the output label will be defaulted to be the "0" label.
  - If the program is a **evaluator** (BOB), it will receive the table through an `IO` and evaluate the table. 

By initializing the two variables with different implementations of the `ProtocolExecution` and `CircuitExecution` interfaces, the program can assume different roles and execute different types of MPC protocols.

Then, you can write the computation part as normal, except the EMP data types (`emp::Integer`, `emp::Bit`, ...) need to be used instead. For example, 

```c++
using namespace emp;

bool int_cmp(int i1, int i2) {
    Integer a(32, i1, ALICE); // 32-bit integer
    Integer b(32, i2, ALICE);

    Bit c;

    c = a > b;

    return c.reveal<bool>(BOB); // reveal to BOB only
}
```


1. When an EMP data object is created, its constructor will call the `ProtocolExecution::feed()` function to initialize the corresponding labels. 
2. When an operation is performed on the data, the operator is overloaded to translate the operation into a boolean circuit and then call the corresponding functions in `CircuitExecution`.
3. When the reveal function is called, it will be redirected to `ProtocolExecution::reveal()` and output the actual value.

## Circuit file generation

By default, EMP-toolkit does not generate the circuit file (which describes how the boolean gates are connected and the types of each gate), since it computes everything on the fly. However, it does provide special implementations of `ProtocolExecution` and `CircuitExecution` through the `setup_plain_prot()` function to generate the circuit file:

```c++
using namespace emp;

setup_plain_prot(true, "circuit.txt");
int_cmp();
finalize_plain_prot();
```

## Links

- [EMP-toolkit's github](https://github.com/emp-toolkit)
- [EMP-toolkit's base repo](https://github.com/emp-toolkit/emp-tool), which includes implementations of data types (`Integer`, `Bit`, ...) and garbled circuit generation/evaluation (used in `CircuitExecution`). 
- [EMP-toolkit's semi-honest 2-party MPC repo](https://github.com/emp-toolkit/emp-sh2pc), which includes implementations of `ProtocolExecution` that are specific to the semi-honest 2-party settings. One example program is included in [./test/ot.cpp](test/ot.cpp).
- The MPC optimizations used in EMP-toolkit includes Point-and-Permute, Free XOR, and Half AND Gate. Some high-level descriptions of these optimizations can be found in [A Gentle Introduction to Yao's Garbled Circuits](http://web.mit.edu/sonka89/www/papers/2017ygc.pdf).
