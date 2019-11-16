#ifndef TAP_CLIENT_CIRC_H
#define TAP_CLIENT_CIRC_H

#include "emp-tool/io/net_io_channel.h"
#include "emp-tool/io/file_io_channel.h"
#include "emp-tool/utils/block.h"
#include "emp-tool/utils/utils.h"
#include "emp-tool/utils/prp.h"
#include "emp-tool/execution/circuit_execution.h"
#include "emp-tool/gc/halfgate_gen.h"
#include <iostream>

namespace emp {
    template<typename T, RTCktOpt rt = on>
    class ClientCircuit: public HalfGateGen<T,RTCktOpt::off> {
    public:

        ClientCircuit(T * io, block * seed) : HalfGateGen<T,RTCktOpt::off>(io)  {
            PRG tmp;
            tmp.reseed(seed);
            tmp.random_block(&this->seed, 1);
            block a;
            tmp.random_block(&a, 1);
            this->set_delta(a);
        }

    };
    template<typename T>
    class ClientCircuit<T,RTCktOpt::off>: public HalfGateGen<T,RTCktOpt::off> {
    public:
        ClientCircuit(T * io, block * seed) {
            this->io = io;
            PRG tmp;
            tmp.reseed(seed);
            tmp.random_block(&this->seed, 1);
            block a;
            tmp.random_block(&a, 1);
            this->set_delta(a);
        }
    };
}


#endif //TAP_CLIENT_CIRC_H
