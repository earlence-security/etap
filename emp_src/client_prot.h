#ifndef TAP_CLIENT_PROT_H
#define TAP_CLIENT_PROT_H

#include <emp-tool/emp-tool.h>
#include <iostream>

namespace emp {
    template<typename IO>
    class ClientProtocol: public ProtocolExecution {
    public:
        IO* dec_io;
        PRG shared_prg;
        ClientProtocol(IO* dec_io, block * seed): ProtocolExecution(ALICE) {
            this->dec_io = dec_io;
            shared_prg.reseed(seed);
        }

        ~ClientProtocol() = default;

        void feed(block * label, int party, const bool* b, int length) {
            if(party == ALICE) {
                shared_prg.random_block(label, length);
            }
        }


        void reveal(bool* b, int party, const block * label, int length) {
            for (int i = 0; i < length; ++i) {
                dec_io->send_block(&label[i], 1);
//                block label_ = xorBlocks(label[i], gc->delta);
//                io2->send_block(&label_, 1);
            }
        }
    };
}


#endif //TAP_CLIENT_PROT_H
