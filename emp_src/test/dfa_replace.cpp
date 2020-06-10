#include <fstream>
#include <string>
#include <iostream>
#include <vector>
#include <bitset>
#include "emp-sh2pc/emp-sh2pc.h"

#include "state.h"
#include "dfa.h"

using namespace emp;


std::vector<bool> string2ascii(const std::string& s) {
    std::vector<bool> b;

    for (char c : s) {
        int ascii = (int)c;
        std::string bitstring = std::bitset<8>(ascii).to_string();

        for (char bi : bitstring) {
            b.push_back(bi == '1');
        }
    }

    return b;
}

std::vector<Bit> get_string_labels(const std::string& s, int length = -1, int party = PUBLIC) {
    std::vector<Bit> x;
    std::vector<bool> b = string2ascii(s);

    for (bool bi : b) {
        x.emplace_back(bi, party);
    }

    if (s.size() < length) {
        for (int i = 0; i < (length - s.size()) * 8; i++) {
            x.emplace_back(false, party);
        }
    }

    return x;
}

Bit start_with(const std::vector<Bit>& x, const std::vector<Bit>& s) {
    Bit m(true);

    for (int i = 0; i < s.size(); i++) {
        m = m & (x[i] == s[i]);
    }

    return m;
}


std::vector<Bit> lookup(const std::vector<Bit>& x,
                        const std::vector<std::vector<Bit>>& k, const std::vector<std::vector<Bit>>& v) {

    std::cout << "wtf" << std::endl;



    std::vector<Bit> m(k.size());
    for (int i = 0; i < m.size(); i++) {
        m[i] = start_with(x, k[i]);
    }

    for (int j = 0; j < k.size(); j++) {
        std::vector<bool> ys;
        std::cout << "m_i: ";
        for (int i = 0; i < m.size(); i++) {
            bool b = m[i].reveal<bool>();
            ys.push_back(b);
            std::cout << b;
            if (i % 8 == 7)
                std::cout << ' ';
        }
        std::cout << std::endl;
    }

    std::vector<Bit> y(v[0].size());

    for (int i = 0; i < m.size(); i++) {
        for (int j = 0; j < y.size(); j++) {
            y[j] = (m[i] & v[i][j]) ^ (!m[i] & y[j]);
        }
    }

    return y;
}


int main(int argc, char** argv) {


    int port, party;
    parse_party_and_port(argv, &party, &port);
    NetIO * io = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);

    setup_semi_honest(io, party);

    auto x_2 = get_string_labels("list3",5, ALICE);

    {
        std::vector<bool> ys;
        std::cout << "x: ";
        for (int i = 0; i < x_2.size(); i++) {
            bool b = x_2[i].reveal<bool>();
            ys.push_back(b);
            std::cout << b;
            if (i % 8 == 7)
                std::cout << ' ';
        }
        std::cout << std::endl;
    }

    std::vector<std::vector<Bit>> k{get_string_labels("list1", 5),
                                    get_string_labels("list2", 5),
                                    get_string_labels("list3", 5),
                                    get_string_labels("list4", 5),
                                    get_string_labels("list5", 5)};


    {
        for (int j = 0; j < k.size(); j++) {
            std::vector<bool> ys;
            std::cout << "k_i: ";
            for (int i = 0; i < k[j].size(); i++) {
                bool b = k[j][i].reveal<bool>();
                ys.push_back(b);
                std::cout << b;
                if (i % 8 == 7)
                    std::cout << ' ';
            }
            std::cout << std::endl;
        }
    }

    std::vector<std::vector<Bit>> v{get_string_labels("list6", 5),
                                           get_string_labels("list7", 5),
                                           get_string_labels("list8", 5),
                                           get_string_labels("list9", 5),
                                           get_string_labels("list0", 5)};

    {
        for (int j = 0; j < k.size(); j++) {
            std::vector<bool> ys;
            std::cout << "v_i: ";
            for (int i = 0; i < k[j].size(); i++) {
                bool b = k[j][i].reveal<bool>(PUBLIC);
                ys.push_back(b);
                std::cout << b;
                if (i % 8 == 7)
                    std::cout << ' ';
            }
            std::cout << std::endl;
        }
    }

    auto y_2 = lookup(x_2, k, v);


    return 0;

//    DFA dfa;
//    dfa.read_from_file("dfa.txt");
//
//    auto x = get_string_labels("babcdabbc!");
//    auto q = dfa.get_initial_states();
//
//
//    std::vector<Int2> t;
//
//    for (auto xi : x) {
//        q = dfa.process(q, xi);
////        for (int qi = 0; qi < q.size(); qi++) {
////            if (q[qi].reveal<bool>())
////                std::cout << qi << std::endl;
////        }
//        t.push_back(dfa.get_state_type(q));
//    }
//
//    auto b = simplify_state_type(t);
//
//    auto y = transform_string(x, b);
//
//    // output y_i
//    std::vector<bool> ys;
//    std::cout << "y_i:" << std::endl;
//    for (int i = 0; i < y.size(); i++) {
//        bool b = y[i].reveal<bool>();
//        ys.push_back(b);
//        std::cout << b;
//        if (i % 8 == 7)
//            std::cout << ' ';
//    }
//    std::cout << std::endl;
//
//
//    return 0;
}
