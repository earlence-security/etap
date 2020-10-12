
#ifndef EMPUTILS__DECODER_PROT_H
#define EMPUTILS__DECODER_PROT_H

namespace emp {
class DecoderProtocol: public ProtocolExecution {
public:
    MemIO* table = nullptr;
    MemIO* output = nullptr;
    FileIO* test;
    DecoderProtocol(const char * labels, const char * dec, int length): ProtocolExecution(BOB) {
        output = new MemIO();
        output->send_block((block *)labels, length);

        table = new MemIO();
        table->send_data(dec, length);
    }

    ~DecoderProtocol() {
    }

    void feed(block * label, int party, const bool* b, int length) {
        output->recv_block(label, length);
    }

    void reveal(bool * b, int party, const block * label, int length) {
        for (int i = 0; i < length; ++i) {
            if(isOne(&label[i]))
                b[i] = true;
            else if (isZero(&label[i]))
                b[i] = false;
            else {
                bool lsb, tmp;
                lsb = (*((char*)&label[i] + 15)&1) == 1;
                table->recv_data(&tmp, 1);
                b[i] = (tmp != lsb);
            }
        }
    }

};
}

#endif //EMPUTILS__DECODER_PROT_H
