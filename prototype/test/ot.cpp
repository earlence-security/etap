#include "emp-sh2pc/emp-sh2pc.h"
#include "client_prot.h"
#include "client_circ.h"
#include <new>
using namespace emp;





int main(int argc, char** argv) {


    // run computation with semi-honest model
    int port, party;
    parse_party_and_port(argv, &party, &port);
    NetIO * io = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);

    setup_semi_honest(io, party);

    Integer a(16, 4, BOB);
    Integer b(16, 5, BOB);

    Integer c(16, 0, PUBLIC);

    c = a + b;

    std::cout << c.reveal<string>() << std::endl;

    FileIO * tmp;
    if (party == ALICE) {
        tmp = new FileIO("alice.txt", false);
    } else {
        tmp = new FileIO("bob.txt", false);
    }
    tmp->send_block((block *)a.bits, 16);
    tmp->send_block((block *)b.bits, 16);
    tmp->send_block((block *)c.bits, 16);

    delete io;
}


