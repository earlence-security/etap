#ifndef TAP_CLIENT_PROT_H
#define TAP_CLIENT_PROT_H

#include <emp-tool/emp-tool.h>
#include <iostream>

namespace emp {
    template<typename IO>
    class ClientProtocol: public ProtocolExecution {
    public:
        IO* io;
        IO* io2;
        PRG prg, shared_prg;
        HalfGateGen<IO> * gc;
        FileIO * tmp;
        ClientProtocol(IO* io, IO* io2, HalfGateGen<IO>* gc, block * seed): ProtocolExecution(ALICE) {
            this->io = io;
            this->io2 = io2;
            this->gc = gc;
            io->send_block(seed, 1);

            io->send_block(&gc->delta, 1);
            shared_prg.reseed(seed);

        }

        ~ClientProtocol() {
        }

        void feed(block * label, int party, const bool* b, int length) {
            if(party == ALICE) {

                shared_prg.random_block(label, length);

            } else {
//                ot->send_cot(label, gc->delta, length);
            }
        }


        void reveal(bool* b, int party, const block * label, int length) {
            for (int i = 0; i < length; ++i) {
                io2->send_block(&label[i], 1);
                block label_ = xorBlocks(label[i], gc->delta);
                io2->send_block(&label_, 1);
            }
        }
    };
}


#endif //TAP_CLIENT_PROT_H
