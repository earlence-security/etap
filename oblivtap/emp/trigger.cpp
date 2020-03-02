#include <emp-tool/emp-tool.h>
#include <pybind11/pybind11.h>

#include "trigger_prot.h"


namespace py = pybind11;


void init(char * seed, char * delta) {
    emp::block seed2, delta2;
    memcpy(seed, &seed2, 16);
    memcpy(delta, &delta2, 16);

    emp::AbandonIO * io = new emp::AbandonIO();
    emp::CircuitExecution::circ_exec = new emp::HalfGateGen<emp::AbandonIO>(io);
    emp::ProtocolExecution::prot_exec = new emp::TriggerProtocol(seed2, delta2);
}


py::bytes encode_bit(bool bit) {
    char * buffer = new char[16];
    emp::Bit b(bit, emp::ALICE);
    memcpy(buffer, &b.bit, 16);
    return py::bytes(buffer, 16);
}


py::bytes encode_int(int num, int length = 32) {
    char * buffer = new char[16 * length];
    emp::Integer i(length, num, emp::ALICE);
    memcpy(buffer, i.bits, 16 * length);
    return py::bytes(buffer, 16 * length);
}


py::bytes test(int i, int j) {
    char * buffer = new char[16];

    emp::PRG prg;
    emp::block label;

    prg.random_block(&label, 1);

    memcpy(buffer, &label, 16);

    return py::bytes(std::string(buffer, 16));
}


PYBIND11_MODULE(dtap_lib, m) {
    py::class_<emp::ProtocolExecution>(m, "ProtocolExecution")
        .def_property_static("prot_exec",
                             nullptr,
                             &init);

    m.def("init", &init);

    m.def("encode_bit", &encode_bit);

    m.def("encode_int", &encode_int);


#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}