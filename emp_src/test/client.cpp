
#include <new>
#include <emp-tool/emp-tool.h>
#include "client_prot.h"

#include "utils.h"
#include "func_reader.h"


using namespace emp;




int main(int argc, char** argv) {


    // argv[2]: encoding data file
    // argv[3]: circuit table file
    // argv[4]: decoding data file
    // argv[5]: dfa directory
    FileIO * enc_io = new FileIO(argv[2], true);
    FileIO * table_io = new FileIO(argv[3], false);
    FileIO * dec_io = new FileIO(argv[4], false);


    block seed, delta;
    enc_io->recv_block(&seed, 1);
    enc_io->recv_block(&delta, 1);

    auto * t = new HalfGateGen<FileIO>(table_io);
    t->set_delta(delta);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new ClientProtocol<FileIO>(dec_io, &seed);


    execute(argv[1], std::stoi(argv[5]));


    delete table_io;
    delete enc_io;
    delete dec_io;
}


