#include "emp-sh2pc/emp-sh2pc.h"
#include "action_prot.h"
#include <new>
using namespace emp;


void emp_bit_and() {

    Bit c(false, BOB);


    std::cout << c.reveal<string>(PUBLIC) << std::endl;
}

void int_add() {
    Integer c(16, 0, BOB);

    std::cout << c.reveal<int>(PUBLIC) << std::endl;
}

void int_cmp() {

    Bit c(false, BOB);

    std::cout << c.reveal<string>(PUBLIC) << std::endl;

}


int main(int argc, char** argv) {


    // run computation with semi-honest model
    int party = BOB;
//    NetIO * input = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);
    FileIO * dec = new FileIO("dec.txt", true);
    FileIO * input = new FileIO("output.txt", true);;

    auto * t = new HalfGateEva<FileIO>(dec);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new ActionProtocol<FileIO>(dec, input);

    int_cmp();

    delete input;
    delete dec;
}


