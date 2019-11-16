#ifndef TAP_CLIENT_PROT_H
#define TAP_CLIENT_PROT_H

#include <emp-tool/emp-tool.h>
#include <iostream>
#include "client_circ.h"

namespace emp {
    template<typename IO>
    class ClientProtocol: public ProtocolExecution {
    public:
        IO* io;
        IO* io2;
        PRG prg, shared_prg;
      ClientCircuit<IO> * gc;
        FileIO * tmp;
        ClientProtocol(IO* io, IO* io2, ClientCircuit<IO>* gc, block * seed): ProtocolExecution(ALICE) {
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
                for (int i = 0; i < length; ++i) {
                    if(b[i])
                        label[i] = xorBlocks(label[i], gc->delta);
                }
            } else {
//                ot->send_cot(label, gc->delta, length);
            }
        }


        void reveal(bool* b, int party, const block * label, int length) {
            for (int i = 0; i < length; ++i) {
                if(isOne(&label[i]))
                    b[i] = true;
                else if (isZero(&label[i]))
                    b[i] = false;
                else {
                    bool lsb = getLSB(label[i]);
                    io2->send_data(&lsb, 1);
                    b[i] = false;
                }
            }
        }
    };
}


#endif //TAP_CLIENT_PROT_H
