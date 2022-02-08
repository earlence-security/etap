#include <emp-tool/emp-tool.h>
#include "trigger_prot.h"
#include <new>
#include <utils.h>

using namespace emp;


std::vector<Bit> get_string_labels(const std::string& s, int length = -1) {
    std::vector<Bit> x;
    std::vector<bool> b = string2ascii(s);

    for (bool bi : b) {
        x.emplace_back(bi, ALICE);
    }

    if (s.size() < length) {
        for (int i = 0; i < (length - s.size()) * 8; i++) {
            x.emplace_back(false, ALICE);
        }
    }

    return x;
}


int main(int argc, char** argv) {

    // run computation with semi-honest model
    FileIO * enc = new FileIO("enc.txt", true);
    FileIO * output = new FileIO("input.txt", false);


    auto * t = new HalfGateGen<FileIO>(enc);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new TriggerProtocol<FileIO>(enc, output);


    int rule_id = std::stoi(argv[1]);

    switch(rule_id) {
        case 1: {
            auto x = get_string_labels(argv[2],140);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 2: {
            auto x = get_string_labels(argv[2],140);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 3: {
            auto x_1 = Integer(32, std::stoi(argv[2]), ALICE);
            auto x_2 = get_string_labels("argv[3]",20);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 4: {
            auto x = get_string_labels(argv[2],30);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 5: {
            auto x = get_string_labels(argv[2],200);
            auto p = Bit(true, ALICE);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 6: {
            auto x = get_string_labels(argv[2],7);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 7: {
            auto x = get_string_labels(argv[2],12);
            auto p = Bit(true, ALICE);
            auto tmp = get_string_labels("", 200);
            break;
        }


        case 8: {
            auto x_1 = get_string_labels(argv[2],20);
            auto x_2 = get_string_labels("argv[3]",50);
            auto p = Bit(true, ALICE);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 9: {
            auto x_1 = Integer(32, std::stoi(argv[2]), ALICE);
            auto x_2 = Integer(32, std::stoi(argv[3]), ALICE);
            auto x_3 = get_string_labels("argv[4]", 50);
            auto p = Bit(true, ALICE);
            auto tmp = get_string_labels("", 200);
            break;
        }

        case 10: {
            auto x_1 = get_string_labels(argv[2],20);
            auto x_2 = get_string_labels("list3",5);
            auto tmp = get_string_labels("", 200);
            break;
        }


        case 100: {
            auto x = Bit(false, ALICE);
            auto c = Bit(false, ALICE);
            break;
        }

        case 101: {
            auto x = Integer(32, 0, ALICE);
            auto c = Integer(32, 0, ALICE);
            break;
        }

        case 102: {
            auto x = Integer(32, 0, ALICE);
            auto c = Integer(32, 0, ALICE);
            break;
        }

        case 103: {
            auto x = get_string_labels("argv[2]",100);
            break;
        }

        case 104: {
            auto x = get_string_labels("argv[2]",100);
            break;
        }

        case 105: {
            auto x = get_string_labels("argv[2]",100);
            break;
        }

        case 106: {
            auto x = get_string_labels("argv[2]",100);
            break;
        }


        case 107: {
            auto x = get_string_labels("argv[2]",100);
            break;
        }

        case 108: {
            auto x = get_string_labels("argv[2]",10);
            break;
        }


        default:
            std::cerr << "Invalid rule id" << rule_id << std::endl;
    }



    delete enc;
    delete output;
}


