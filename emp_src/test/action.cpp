#include <emp-tool/emp-tool.h>
#include "action_prot.h"
#include <new>
#include <utils.h>

using namespace emp;


void dfa_replace(int string_length) {

    std::vector<Bit> y;

    for (int i = 0; i < string_length * 8; i++) {
        y.emplace_back(false, BOB);
    }

    std::vector<bool> ys;
    std::cout << "output bit string: ";
    for (int i = 0; i < y.size(); i++) {
        bool b = y[i].reveal<bool>();
        ys.push_back(b);
        std::cout << b;
        if (i % 8 == 7)
            std::cout << ' ';
    }
    std::cout << std::endl;
    std::cout << "output string: " << ascii2string(ys) << std::endl;

}

std::vector<Bit> get_string_labels(int string_length) {
    std::vector<Bit> y;

    for (int i = 0; i < string_length * 8; i++) {
        y.emplace_back(false, BOB);
    }

    return y;
}


int main(int argc, char** argv) {

    // run computation with semi-honest model
    int party = BOB;
//    NetIO * input = new NetIO(party==ALICE ? nullptr : "127.0.0.1", port);
    FileIO * dec = new FileIO("dec.txt", true);
    FileIO * input = new FileIO("output.txt", true);


    auto * t = new HalfGateEva<FileIO>(dec);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new ActionProtocol<FileIO>(dec, input);

    int rule_id = std::stoi(argv[1]);

    switch(rule_id) {
        case 1: {
            auto p = Bit(false, BOB);
            auto y = get_string_labels(144);

            std::cout << p.reveal<string>() << std::endl;
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 2: {
            auto p = Bit(false, BOB);
            auto y = get_string_labels(144);

            std::cout << p.reveal<string>() << std::endl;
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 3: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 4: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 5: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 6: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }


        case 8: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 9: {
            auto y = get_string_labels(20);

            std::vector<bool> ys;
            for (int i = 0; i < y.size(); i++) {
                bool b = y[i].reveal<bool>();
                ys.push_back(b);
                std::cout << b;
                if (i % 8 == 7)
                    std::cout << ' ';
            }
            std::cout << std::endl;
            std::cout << ascii2string(ys) << std::endl;
            break;
        }

        case 11: {
            auto y1 = get_string_labels(30);
            auto y2 = get_string_labels(30);

            for (auto y1i : y1)
                y1i.reveal<bool>();
            for (auto y2i : y2)
                y2i.reveal<bool>();
            break;
        }

        case 12: {
            auto y = Integer(32, 0, BOB);

            y.reveal<int>();
            break;
        }


        case 14: {
            auto y = get_string_labels(1000);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 16: {
            auto p = Bit(false, BOB);
            auto y = get_string_labels(144);

            std::cout << p.reveal<string>() << std::endl;

            std::vector<bool> ys;
            for (int i = 0; i < y.size(); i++) {
                bool b = y[i].reveal<bool>();
                ys.push_back(b);
                std::cout << b;
                if (i % 8 == 7)
                    std::cout << ' ';
            }
            std::cout << std::endl;
            std::cout << ascii2string(ys) << std::endl;
            break;
        }

        case 101: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 102: {
            auto y = Integer(32, 0, BOB);

            y.reveal<int>();
            break;
        }

        case 103: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        case 104: {
            auto y = get_string_labels(1000);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 105: {
            auto p = Bit(false, BOB);

            std::cout << p.reveal<string>() << std::endl;
            break;
        }

        default:
            std::cout << "Invalid rule id" << rule_id << std::endl;
    }


    delete input;
    delete dec;
}


