
#ifndef DTAP_LIB__TRIGGER_PROT_H
#define DTAP_LIB__TRIGGER_PROT_H

namespace emp {


class TriggerProtocol: public ProtocolExecution {
public:
    block delta;
    PRG shared_prg;
    TriggerProtocol(block seed, block delta) {
        shared_prg.reseed(&seed);
        this->delta = delta;
    }

    ~TriggerProtocol() {
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


#endif //DTAP_LIB__TRIGGER_PROT_H
