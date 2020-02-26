
#ifndef TAP_TRIGGER_PROT_H
#define TAP_TRIGGER_PROT_H

namespace emp {
    template<typename IO>
    class TriggerProtocol: public ProtocolExecution {
    public:
        IO* input = nullptr;
        IO* output = nullptr;
        block delta;
        PRG shared_prg;
        TriggerProtocol(IO *input, IO *output): ProtocolExecution(ALICE) {
            this->input = input;
            this->output = output;
            block seed; input->recv_block(&seed, 1);
            shared_prg.reseed(&seed);

            input->recv_block(&(this->delta), 1);
        }

        ~TriggerProtocol() {
        }

        void feed(block * label, int party, const bool* b, int length) {
            if(party == ALICE) {
                shared_prg.random_block(label, length);
                for (int i = 0; i < length; ++i) {
                    if (b[i])
                        label[i] = xorBlocks(label[i], delta);
                }
                output->send_block(label, length);
            } else {
//                ot->recv_cot(label, b, length);
            }
        }

        void reveal(bool * b, int party, const block * label, int length) {

        }

    };
}



#endif //TAP_TRIGGER_PROT_H
