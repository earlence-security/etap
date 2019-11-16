
#ifndef TAP_ACTION_PROT_H
#define TAP_ACTION_PROT_H

namespace emp {
    template<typename IO>
    class ActionProtocol: public ProtocolExecution {
    public:
        IO* table = nullptr;
        IO* input = nullptr;
        PRG shared_prg;
        ActionProtocol(IO *table, IO *input): ProtocolExecution(BOB) {
            this->table = table;
            this->input = input;
            block seed;
//            table->recv_block(&seed, 1);
            shared_prg.reseed(&seed);

        }

        ~ActionProtocol() {
        }

        void feed(block * label, int party, const bool* b, int length) {
            input->recv_block(label, length);
        }

        void reveal(bool * b, int party, const block * label, int length) {
            if (party == XOR) {
                for (int i = 0; i < length; ++i) {
                    if (isOne(&label[i]))
                        b[i] = true;
                    else if (isZero(&label[i]))
                        b[i] = false;
                    else
                        b[i] = getLSB(label[i]);
                }
                return;
            }
            for (int i = 0; i < length; ++i) {
                if(isOne(&label[i]))
                    b[i] = true;
                else if (isZero(&label[i]))
                    b[i] = false;
                else {
                    bool lsb = getLSB(label[i]), tmp;
                    table->recv_data(&tmp, 1);
                    b[i] = (tmp != lsb);
                }
            }
        }

    };
}


#endif //TAP_ACTION_PROT_H
