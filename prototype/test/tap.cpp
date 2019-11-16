#include "emp-sh2pc/emp-sh2pc.h"
#include "tap_prot.h"
#include <new>
using namespace emp;


void emp_bit_and() {
//    Bit a(false, ALICE);
//    Bit b(false, ALICE);
//
//    Bit c;
//
//
//  string file = "and.circuit.txt";
//  CircuitFile cf(file.c_str());
//
//  cf.compute(&c.bit, &a.bit, &b.bit);
//
//  c.reveal<string>(PUBLIC);
    Bit a(false, ALICE);
    Bit b(false, ALICE);
    Bit d(false, ALICE);


    Bit c;

    c = (a & b) & d;

    c.reveal<string>();
}

void int_add() {
    Integer a(16, 0, ALICE);
    Integer b(16, 0, ALICE);

    Integer c(16, 0, PUBLIC);

    c = a + b;

    c.reveal<string>(PUBLIC);
}

void int_cmp() {
    Integer a(16, 0, ALICE);
    Integer b(16, 0, ALICE);

    Bit c;

    c = a > b;

    c.reveal<string>();

}


int main(int argc, char** argv) {


    int party = BOB;
//    NetIO * input = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);
    FileIO * table = new FileIO("table.txt", true);
    FileIO * input = new FileIO("input.txt", true);
    FileIO * output = new FileIO("output.txt", false);

    auto * t = new HalfGateEva<FileIO>(table);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new CloudProtocol<FileIO>(table, input, output);

    int_cmp();

    delete input;
    delete output;
}


