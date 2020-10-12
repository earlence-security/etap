
#ifndef EMPUTILS__ENCODER_PROT_H
#define EMPUTILS__ENCODER_PROT_H

namespace emp {


class EncoderProtocol: public ProtocolExecution {
public:
    block delta;
    PRG shared_prg;
    EncoderProtocol(block seed, block delta) {
        shared_prg.reseed(&seed);
        this->delta = make_delta(delta);
    }

    ~EncoderProtocol() {
    }

    void feed(block * label, int party, const bool* b, int length) {
        shared_prg.random_block(label, length);
        for (int i = 0; i < length; ++i) {
            if (b[i])
                label[i] = xorBlocks(label[i], delta);
        }
    }

    void reveal(bool * b, int party, const block * label, int length) {}

};
}


#endif //EMPUTILS__ENCODER_PROT_H
