
#ifndef EMPUTILS__DUMMY_CIRC_H
#define EMPUTILS__DUMMY_CIRC_H

namespace emp
{
class DummyCircExec : public CircuitExecution
{
public:

    DummyCircExec() = default;

    block
    public_label(bool b) override
    {
        return zero_block();
    }
    block
    and_gate(const block &a, const block &b) override
    {
        return zero_block();
    }
    block
    xor_gate(const block &a, const block &b) override
    {
        return zero_block();
    }
    block
    not_gate(const block &a) override
    {
        return zero_block();
    }

};

}

#endif //EMPUTILS__DUMMY_CIRC_H
