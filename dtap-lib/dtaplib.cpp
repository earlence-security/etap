#include <bitset>
#include <vector>

#include <emp-tool/emp-tool.h>
#include <pybind11/pybind11.h>

#include "trigger_prot.h"
#include "action_prot.h"
#include "dummy_circ.h"

namespace py = pybind11;


void trigger_init(const char * seed, const char * delta) {
    emp::CircuitExecution::circ_exec = new emp::DummyCircExec();
    emp::ProtocolExecution::prot_exec =
        new emp::TriggerProtocol(*(emp::block *)seed, *(emp::block *)delta);
}

void action_init(const char * labels, const char * dec, int length) {
    emp::CircuitExecution::circ_exec = new emp::DummyCircExec();
    emp::ProtocolExecution::prot_exec =
        new emp::ActionProtocol(labels, dec, length);
}


py::bytes encode_bit(bool bit) {
    char * buffer = new char[16];
    emp::Bit b(bit, emp::ALICE);
    memcpy(buffer, &b.bit, 16);
    return py::bytes(buffer, 16);
}


bool decode_bit() {
    emp::Bit b(false, emp::BOB);
    return b.reveal<bool>();
}


py::bytes encode_int(int num, int size = 32) {
    char * buffer = new char[16 * size];
    emp::Integer i(size, num, emp::ALICE);
    memcpy(buffer, i.bits, 16 * size);
    return py::bytes(buffer, 16 * size);
}


int decode_int(int size = 32) {
    emp::Integer i(size, 0, emp::BOB);
    return i.reveal<int>();
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



py::bytes encode_ascii_str(const std::string& str, int length = -1) {
    int num_bits = std::max((int)str.size(), length) * 8;
    char * buffer = new char[16 * num_bits];
    char * ptr = buffer;

    std::vector<emp::Bit> x;
    std::vector<bool> b = string2ascii(str);

    for (bool bi : b) {
        emp::Bit tmp(bi, emp::ALICE);
        memcpy(ptr, &tmp.bit, 16);
        ptr += 16;
    }

    if ((int)str.size() < length) {
        for (int i = 0; i < (length - str.size()) * 8; i++) {
            emp::Bit tmp(false, emp::ALICE);
            memcpy(ptr, &tmp.bit, 16);
            ptr += 16;
        }
    }

    return py::bytes(buffer, 16 * num_bits);
}


std::string decode_ascii_str(int length) {

    std::vector<emp::Bit> x(length * 8);
    std::vector<bool> b;

    for (auto & xi : x) {
        b.push_back(xi.reveal<bool>());
    }

    return ascii2string(b);
}


py::bytes xor_block(const char * x, const char * y) {
    emp::block z;
    z = _mm_xor_si128(*(emp::block *)x, *(emp::block *)y);
    return py::bytes((char *) &z, 16);
}


py::bytes test(int i, int j) {
    char * buffer = new char[16];

    emp::PRG prg;
    emp::block label;

    prg.random_block(&label, 1);

    memcpy(buffer, &label, 16);

    return py::bytes(std::string(buffer, 16));
}

PYBIND11_MODULE(dtaplib, m) {
    // helper
    py::class_<emp::ProtocolExecution>(m, "ProtocolExecution")
        .def_property_static("prot_exec",
                             nullptr,
                             &trigger_init);

    // trigger functions
    m.def("trigger_init", &trigger_init, py::arg("seed"), py::arg("delta"));

    m.def("encode_bit", &encode_bit);

    m.def("encode_int", &encode_int, py::arg("num"), py::arg("size") = 32);

    m.def("encode_ascii_str", &encode_ascii_str, py::arg("str"), py::arg("length") = -1);

    // action functions
    m.def("action_init", &action_init, py::arg("labels"), py::arg("dec"), py::arg("length"));

    m.def("decode_bit", &decode_bit);

    m.def("decode_int", &decode_int, py::arg("size") = 32);

    m.def("decode_ascii_str", &decode_ascii_str, py::arg("length"));

    // utils
    m.def("xor", &xor_block);


#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}