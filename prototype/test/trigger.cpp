#include "emp-sh2pc/emp-sh2pc.h"
#include "trigger_prot.h"
#include <new>
using namespace emp;


void emp_bit_and(bool b1, bool b2, bool b3) {
    Bit a(b1, ALICE);
    Bit b(b2, ALICE);
    Bit d(b3, ALICE);

}

void int_add(int i1, int i2) {
    Integer a(16, i1, ALICE);
    Integer b(16, i2, ALICE);
}

void int_cmp(int i1, int i2) {
    Integer a(16, i1, ALICE);
    Integer b(16, i2, ALICE);

}

int main(int argc, char** argv) {


    // run computation with semi-honest model
    int party = ALICE;
//    NetIO * input = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);
    FileIO * enc = new FileIO("enc.txt", true);
    FileIO * output = new FileIO("input.txt", false);

    auto * t = new HalfGateGen<FileIO>(enc);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new TriggerProtocol<FileIO>(enc, output);

    int i1, i2;

    i1 = atoi(argv[1]);
    i2 = atoi(argv[2]);

//    emp_bit_and(i1 > 0 , i2 > 0 , atoi(argv[2]) > 0);
    int_cmp(i1, i2);

    delete enc;
    delete output;
}

//
// Created by chenx on 10/21/2019.
//

