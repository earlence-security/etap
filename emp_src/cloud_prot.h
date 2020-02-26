#ifndef TAP_CLOUD_PROT_H
#define TAP_CLOUD_PROT_H

namespace emp {
    template<typename IO>
    class CloudProtocol: public ProtocolExecution {
    public:
        IO* table = nullptr;
        IO* input = nullptr;
        IO* output = nullptr;
        CloudProtocol(IO* table, IO *input, IO *output): ProtocolExecution(BOB) {
            this->table = table;
            this->input = input;
            this->output = output;
        }

        ~CloudProtocol() {
        }

        void feed(block * label, int party, const bool* b, int length) {
            input->recv_block(label, length);
        }

        void reveal(bool * b, int party, const block * label, int length) {
            if(party == PUBLIC) {
                for (int i = 0; i < length; ++i) {
                    output->send_block(&label[i], 1);
                }
            }
        }

    };
}


#endif //TAP_CLOUD_PROT_H
