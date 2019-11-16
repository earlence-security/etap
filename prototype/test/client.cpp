#include "emp-sh2pc/emp-sh2pc.h"
#include "client_prot.h"
#include "client_circ.h"
#include <new>
using namespace emp;


void emp_bit_and() {
    Bit a(false, ALICE);
    Bit b(false, ALICE);
    Bit d(false, ALICE);


    Bit c;

    c = (a & b) & d;

    c.reveal<string>();
}

void int_add() {
    Integer a(32, 0, ALICE);
    Integer b(32, 12, PUBLIC);

    Integer c(32, 0, PUBLIC);

    c = a + b;

//    FileIO * f = new FileIO("client.txt", false);
//    f->send_block((block *)a.bits, 16);
//    f->send_block((block *)b.bits, 16);
//    f->send_block((block *)c.bits, 16);

    c.reveal<string>();

}

void int_cmp() {
    Integer a(32, 0, ALICE);
    Integer b(32, 12, PUBLIC);

    Bit c;

    c = a > b;

    c.reveal<string>();

}


int main(int argc, char** argv) {

    // generate circuit for use in malicious library
    setup_plain_prot(true, "circuit.txt");
    int_cmp();
    finalize_plain_prot();


    // run computation with semi-honest model
    int party = ALICE;
//    NetIO * input = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);
    FileIO * io = new FileIO("table.txt", false);
    FileIO * enc = new FileIO("enc.txt", false);
    FileIO * dec = new FileIO("dec.txt", false);

    block seed = one_block();
    auto * t = new ClientCircuit<FileIO>(io, &seed);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new ClientProtocol<FileIO>(enc, dec, t, &seed);

    int_cmp();

    delete io;
    delete enc;
    delete dec;
}


