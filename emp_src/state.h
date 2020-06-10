
#ifndef TAP_STATE_H
#define TAP_STATE_H

#include <vector>
#include <emp-tool/emp-tool.h>

using namespace emp;

class State {
public:
    State(int number) : number(number) {

    }

    void set_type(int t) {
        type = t;
    }

    Bit process(const std::vector<Bit>& q, const Bit&  x) {
        Bit q_;

        Bit tmp1(false);
        if (!parents_0.empty()) {
            for (int i : parents_0) {
                tmp1 = tmp1 ^ q[i];
            }
//            tmp1 = !x & tmp1;
        }

        Bit tmp2(false);
        if (!parents_1.empty()) {
            for (int i : parents_1) {
                tmp2 = tmp2 ^ q[i];
            }
//            tmp2 = x & tmp2;
        }

        Bit tmp3(false);
        if (!parents_01.empty()) {
            for (int i : parents_01) {
                tmp3 = tmp3 ^ q[i];
            }
        }

        q_ = tmp1.select(x, tmp2) ^ tmp3;

//        q_ = tmp1 ^ tmp2 ^ tmp3;
        return q_;
    }


    int number;
    int type;
    std::vector<int> parents_0;
    std::vector<int> parents_1;
    std::vector<int> parents_01;
};


#endif //TAP_STATE_H
