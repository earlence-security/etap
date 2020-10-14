//
// Created by chenx on 1/4/2020.
//

#ifndef TAP_UTILS_H
#define TAP_UTILS_H

#include <fstream>
#include <string>
#include <iostream>
#include <vector>
#include <bitset>
#include "state.h"
#include "dfa.h"

using namespace emp;
using String = std::vector<Bit>;


std::vector<State> read_dfa(char* fname) {
    std::ifstream dfa_file(fname);

    std::vector<State> dfa;

    int num_states;
    dfa_file >> num_states;

    dfa.reserve(num_states);
    for (int i = 0; i < num_states; i++) {
        dfa.emplace_back(i);
    }


    int q_i, to_0, to_1, type;
    while (dfa_file >> q_i >> to_0 >> to_1 >> type) {
        std::cout << q_i << ' ' << to_0 << ' ' << to_1 << ' ' << type << std::endl;
        if (to_0 == to_1) {
            dfa[to_0].parents_01.push_back(q_i);
        } else {
            dfa[to_0].parents_0.push_back(q_i);
            dfa[to_1].parents_1.push_back(q_i);
        }
        dfa[q_i].set_type(type);
    }

    return dfa;
}


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


std::string ascii2string(const std::vector<bool>& b) {
    std::string s;

    for (int i = 0; i < b.size(); i += 8) {
        int ascii = 0;
        for (int j = 0; j < 8; j++) {
            if (b[i+7-j]) {
                ascii += pow(2, j);
            }
        }
        s.push_back((char) ascii);
    }

    return s;
}




std::vector<Bit> find_match(const std::vector<Bit>& start, const std::vector<Bit>& end) {
    int n = start.size();
    std::vector<Bit> m(n);


    for (int i = n - 1; i >= 0; i--) {
        if (i == n - 1) {
            m[i] = end[i];
        } else {
            m[i] = end[i] | (!start[i+1] & m[i+1]);
        }
    }

    return m;
}


std::vector<Bit> find_first(const std::vector<Bit>& d) {
    int n = d.size();
    std::vector<Bit> m(n);

    m[0] = Bit(true);
    for (int i = 1; i < n; i++) {
        m[i] = m[i-1] & ! d[i];
    }

    return m;
}


std::vector<Bit> find_last(const std::vector<Bit>& d) {
    int n = d.size();
    std::vector<Bit> m(n);

    m[n-1] = Bit(true);
    for (int i = n-2; i >= 0; i--) {
        m[i] = m[i+1] & ! d[i];
    }

    return m;
}



std::vector<Bit> remove_match(const std::vector<Bit>& m, const std::vector<Bit>& x) {
    std::vector<Bit> y(x.size());
    for (int i = 0; i < x.size(); i++) {
        y[i] = !m[i/8] & x[i];
    }
    return y;
}

std::vector<Bit> extract_match(const std::vector<Bit>& m, const std::vector<Bit>& x) {
    std::vector<Bit> y(x.size());
    for (int i = 0; i < x.size(); i++) {
        y[i] = m[i/8] & x[i];
    }
    return y;
}


std::vector<Bit> add_replacement(const std::vector<Bit>& s, const std::vector<Bit>& x) {
    std::vector<Bit> y(x.size());
    for (int i = 0; i < x.size(); i++) {
        y[i] = s[i] | x[i];
    }
    return y;
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

    std::vector<Bit> m(k.size());
    for (int i = 0; i < m.size(); i++) {
        m[i] = start_with(x, k[i]);
    }

    std::vector<Bit> y(v[0].size());

    for (int i = 0; i < m.size(); i++) {
        for (int j = 0; j < y.size(); j++) {
            y[j] = (m[i] & v[i][j]) ^ (!m[i] & y[j]);
        }
    }

    return y;
}



std::vector<Bit> dfa_extract(const std::string& dfa_file, const std::string& r_dfa_file, const std::vector<Bit>& x) {

    DFA dfa;
    dfa.read_from_file(dfa_file);

    DFA r_dfa;
    r_dfa.read_from_file(r_dfa_file);

    auto q = dfa.get_initial_states();
    auto q_ = r_dfa.get_initial_states();

    std::vector<Bit> end;

    for (int i = 0; i < x.size(); i++) {
        q = dfa.process(q, x[i]);
        if (i % 8 == 7) {
            end.push_back(dfa.is_accept_state(q));
        }
    }

    std::vector<Bit> start;

    for (int i = x.size()-1; i >= 0; i--) {
        q_ = r_dfa.process(q_, x[i]);
        if (i % 8 == 0) {
            start.push_back(r_dfa.is_accept_state(q_));
        }
    }

    std::reverse(start.begin(), start.end());

    auto m = find_match(start, end);

    auto y = extract_match(m, x);

    return y;

}


Bit dfa_match(const std::string& dfa_file, const std::vector<Bit>& x) {

    DFA dfa;
    dfa.read_from_file(dfa_file);

    auto q = dfa.get_initial_states();


    for (auto xi : x) {
        q = dfa.process(q, xi);
    }

    return dfa.is_accept_state(q);
}


std::vector<Bit> dfa_remove(const std::string& dfa_file, const std::string& r_dfa_file, const std::vector<Bit>& x) {

    DFA dfa;
    dfa.read_from_file(dfa_file);

    DFA r_dfa;
    r_dfa.read_from_file(r_dfa_file);

    auto q = dfa.get_initial_states();
    auto q_ = r_dfa.get_initial_states();

    std::vector<Bit> end;

    for (int i = 0; i < x.size(); i++) {
        q = dfa.process(q, x[i]);
        if (i % 8 == 7) {
            end.push_back(dfa.is_accept_state(q));
        }
    }

    std::vector<Bit> start;

    for (int i = x.size()-1; i >= 0; i--) {
        q_ = r_dfa.process(q_, x[i]);
        if (i % 8 == 0) {
            start.push_back(r_dfa.is_accept_state(q_));
        }
    }

    std::reverse(start.begin(), start.end());

    auto m = find_match(start, end);

    auto y = remove_match(m, x);

    return y;

}


std::vector<Bit> dfa_remove_single_char(const std::string& dfa_file, const std::vector<Bit>& x) {

    DFA dfa;
    dfa.read_from_file(dfa_file);

    auto q = dfa.get_initial_states();

    std::vector<Bit> m;

    for (int i = 0; i < x.size(); i++) {
        q = dfa.process(q, x[i]);
        if (i % 8 == 7) {
            m.push_back(dfa.is_accept_state(q));
        }
    }

    auto y = remove_match(m, x);

    return y;

}


std::vector<Bit> dfa_find_single_char(const std::string& dfa_file, const std::vector<Bit>& x) {

    DFA dfa;
    dfa.read_from_file(dfa_file);

    auto q = dfa.get_initial_states();

    std::vector<Bit> m;

    for (int i = 0; i < x.size(); i++) {
        q = dfa.process(q, x[i]);
        if (i % 8 == 7) {
            m.push_back(dfa.is_accept_state(q));
        }
    }

    return m;

}



std::vector<Bit> split(const std::string& dfa_file, const std::vector<Bit>& x, int index) {
    auto d = dfa_find_single_char(dfa_file, x);

    if (index == 0) {
        auto m = find_first(d);
        auto y = extract_match(m, x);
        return y;
    } else if (index == -1) {
        auto m = find_last(d);
        auto y = extract_match(m, x);
        return y;
    } else {
        std::cerr << "Not impelmented" << std::endl;
        return {};
    }
}







#endif //TAP_UTILS_H
