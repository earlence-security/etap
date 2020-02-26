
#ifndef TAP_DFA_H
#define TAP_DFA_H

#include <emp-tool/emp-tool.h>
#include "state.h"

using namespace emp;

class DFA {
public:
    void read_from_file(const char* fname) {
        std::ifstream dfa_file(fname);

        int num_states;
        dfa_file >> num_states >> initial;

        states.reserve(num_states);
        for (int i = 0; i < num_states; i++) {
            states.emplace_back(i);
        }

        int q_i, to_0, to_1, type;
        while (dfa_file >> q_i >> to_0 >> to_1 >> type) {
            if (to_0 == to_1) {
                states[to_0].parents_01.push_back(q_i);
            } else {
                states[to_0].parents_0.push_back(q_i);
                states[to_1].parents_1.push_back(q_i);
            }
            states[q_i].set_type(type);
        }
    }

    int size() {
        return states.size();
    }

    std::vector<Bit> process(const std::vector<Bit>& q, const Bit&  x) {
        std::vector<Bit> q_;
        for (State state : states) {
            q_.push_back(state.process(q, x));
        }
        return q_;
    }

    std::vector<Bit> get_initial_states() {
        std::vector<Bit> q;
        for (int i = 0; i < states.size(); i++) {
            q.emplace_back(i == initial, PUBLIC);
        }
        return q;
    }



    Bit is_accept_state(const std::vector<Bit>& q) {
        std::vector<int> accept_states;

        for (const State& state : states) {
            if (state.type == 1) {
                accept_states.push_back(state.number);
            }
        }

        Bit b;

        for (int i : accept_states) {
            b = b ^ q[i];
        }

        return b;
    }




    std::vector<State> states;
    int initial;
};


#endif //TAP_DFA_H
