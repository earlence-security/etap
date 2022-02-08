#include <new>

#include <emp-tool/emp-tool.h>
#include "cloud_prot.h"

#include "dfa.h"
#include "utils.h"
#include "func_reader.h"


using namespace emp;




int main(int argc, char** argv) {


    // argv[2]: circuit table file
    // argv[3]: input label file
    // argv[4]: output label file
    // argv[5]: dfa directory
    FileIO * table_io = new FileIO(argv[2], true);
    FileIO * input_io = new FileIO(argv[3], true);
    FileIO * output_io = new FileIO(argv[4], false);


    auto * t = new HalfGateEva<FileIO>(table_io);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new CloudProtocol<FileIO>(input_io, output_io);

    execute(argv[1]);



    delete table_io;
    delete input_io;
    delete output_io;
}


