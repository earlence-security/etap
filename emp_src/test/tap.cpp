#include "emp-sh2pc/emp-sh2pc.h"
#include "cloud_prot.h"
#include <new>
#include <dfa.h>
#include <utils.h>
using namespace emp;



std::vector<Bit> get_empty_string_labels(int length) {
    std::vector<Bit> x;

    for (int i = 0; i < length * 8; i++) {
        x.emplace_back(false, ALICE);
    }
    return x;
}


std::vector<Bit> get_string_labels(const std::string& s, int length = -1, int party = PUBLIC) {
    std::vector<Bit> x;
    std::vector<bool> b = string2ascii(s);

    for (bool bi : b) {
        x.emplace_back(bi, party);
    }

    if ((int)s.size() < length) {
        for (int i = 0; i < (length - s.size()) * 8; i++) {
            x.emplace_back(false, party);
        }
    }

    return x;
}




int main(int argc, char** argv) {


    // argv[2]: circuit table file
    // argv[3]: input label file
    // argv[4]: output label file
    // argv[5]: dfa directory
    FileIO * table_io = new FileIO(argv[2], true);
    FileIO * input_io = new FileIO(argv[3], true);
    FileIO * output_io = new FileIO(argv[4], false);
    std::string dfa_dir(argv[5]);


    auto * t = new HalfGateEva<FileIO>(table_io);
    CircuitExecution::circ_exec = t;
    ProtocolExecution::prot_exec = new CloudProtocol<FileIO>(input_io, output_io);

    int rule_id = std::stoi(argv[1]);

    switch(rule_id) {
        case 1: {
            auto x = get_empty_string_labels(140);

            auto p = dfa_match(dfa_dir + "/dfa1.txt", x);
            auto y = x;

            p.reveal<bool>();
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 2: {
            auto x = get_empty_string_labels(140);
            auto c = get_string_labels("@");

            auto p = !start_with(x, c);
            auto y = x;

            p.reveal<bool>();
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 3: {
            auto x_1 = Integer(32, 0, ALICE);
            auto c = Integer(32, 4999, PUBLIC);
            auto x_2 = get_empty_string_labels(20);

            auto p = x_1 > c;
            auto y = x_2;

            p.reveal<bool>();
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 4: {
            auto x = get_empty_string_labels(30);
            auto c = get_string_labels("someone@someaddress.com");

            auto p = start_with(x, c);

            p.reveal<bool>();
            auto y = x;
            for (int i = 0; i < 80; i++)
                y[i].reveal<bool>();
            break;
        }

        case 5: {
            auto x = get_empty_string_labels(200);

            auto p = Bit(false, ALICE);
            auto y = dfa_extract(dfa_dir + "/dfa5.txt", dfa_dir + "/dfa5_2.txt", x);

            p.reveal<bool>();
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 6: {
            auto x = get_empty_string_labels(7);

//            auto p1 = dfa_match(dfa_dir + "/dfa6_1.txt", x);
//            auto p2 = dfa_match(dfa_dir + "/dfa6_2.txt", x);
//            auto p3 = dfa_match(dfa_dir + "/dfa6_3.txt", x);
//            auto p = p1 | p2 | p3;
            auto p = dfa_match(dfa_dir + "/dfa6.txt", x);

            p.reveal<bool>();
            auto y = x;
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 7: {
            auto x = get_empty_string_labels(12);

            auto p = Bit(false, ALICE);
            auto y = dfa_remove_single_char(dfa_dir + "/dfa7.txt", x);

            p.reveal<bool>();
            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }


        case 8: {
            auto x_1 = get_empty_string_labels(20);
            auto x_2 = get_empty_string_labels(50);

            auto p = Bit(false, ALICE);
            auto y_1 = split(dfa_dir + "/dfa8.txt", x_1, 1);
            auto y_2 = split(dfa_dir + "/dfa8.txt", x_1, -1);
            auto y_3 = x_2;

            p.reveal<bool>();
            for (auto yi : y_1)
                yi.reveal<bool>();
            for (auto yi : y_2)
                yi.reveal<bool>();
            for (auto yi : y_3)
                yi.reveal<bool>();
            break;
        }

        case 9: {
            auto x_1 = Integer(32, 0, ALICE);
            auto x_2 = Integer(32, 0, ALICE);
            auto x_3 = get_empty_string_labels(50);

            auto p = Bit(false, ALICE);
            auto y_1 = x_2 - x_1;
            auto y_2 = x_3;

            p.reveal<bool>();
            y_1.reveal<string>();
            for (auto yi : y_2)
                yi.reveal<bool>();
            break;
        }

        case 10: {
            auto x_1 = get_empty_string_labels(20);
            auto x_2 = get_empty_string_labels(5);
            auto s = get_string_labels("$request");
            std::vector<std::vector<Bit>> k{get_string_labels("list1", 5),
                                            get_string_labels("list2", 5),
                                            get_string_labels("list3", 5),
                                            get_string_labels("list4", 5),
                                            get_string_labels("list5", 5)};
            std::vector<std::vector<Bit>> v{get_string_labels("list6", 5),
                                            get_string_labels("list7", 5),
                                            get_string_labels("list8", 5),
                                            get_string_labels("list9", 5),
                                            get_string_labels("list0", 5)};

            auto p = start_with(x_1, s);
            auto y_1 = dfa_remove(dfa_dir + "/dfa10_1.txt", dfa_dir + "/dfa10_1r.txt", x_1);
            auto y_2 = lookup(x_2, k, v);

            p.reveal<bool>();
            for (auto yi : y_1)
                yi.reveal<bool>();
            for (auto yi : y_2)
                yi.reveal<bool>();
            break;
        }



        case 100: {
            auto x = Bit(false, ALICE);
            auto c = Bit(false, ALICE);

            auto p = x & c;

            p.reveal<bool>();
            break;
        }

        case 101: {
            auto x = Integer(32, 0, ALICE);
            auto c = Integer(32, 0, ALICE);

            auto p = x > c;

            p.reveal<bool>();
            break;
        }

        case 102: {
            auto x = Integer(32, 0, ALICE);
            auto c = Integer(32, 0, ALICE);

            auto y = x * c;

            y.reveal<int>();
            break;
        }

        case 103: {
            auto x = get_empty_string_labels(100);

            auto p = dfa_match(dfa_dir + "/dfa1.txt", x);

            p.reveal<bool>();
            break;
        }

        case 104: {
            auto x = get_empty_string_labels(100);

            auto y = dfa_remove(dfa_dir + "/dfa104.txt", dfa_dir + "/dfa104.txt", x);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 105: {
            auto x = get_empty_string_labels(100);

            auto y = split(dfa_dir + "/dfa8.txt", x, 1);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }

        case 106: {
            auto x = get_empty_string_labels(100);

            auto y = dfa_extract(dfa_dir + "/dfa5.txt", dfa_dir + "/dfa5_2.txt", x);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }


        case 107: {
            auto x = get_empty_string_labels(100);
            auto s = get_string_labels("", 100);

            auto p = start_with(x, s);

            p.reveal<bool>();
            break;
        }

        case 108: {
            auto x = get_empty_string_labels(10);
            std::vector<std::vector<Bit>> k{get_string_labels("list1", 10),
                                            get_string_labels("list2", 10),
                                            get_string_labels("list3", 10),
                                            get_string_labels("list4", 10),
                                            get_string_labels("list5", 10),
                                            get_string_labels("list1", 10),
                                            get_string_labels("list2", 10),
                                            get_string_labels("list3", 10),
                                            get_string_labels("list4", 10),
                                            get_string_labels("list5", 10)};
            std::vector<std::vector<Bit>> v{get_string_labels("list6", 10),
                                            get_string_labels("list7", 10),
                                            get_string_labels("list8", 10),
                                            get_string_labels("list9", 10),
                                            get_string_labels("list0", 10),
                                            get_string_labels("list6", 10),
                                            get_string_labels("list7", 10),
                                            get_string_labels("list8", 10),
                                            get_string_labels("list9", 10),
                                            get_string_labels("list0", 10)};

            auto y = lookup(x, k, v);

            for (auto yi : y)
                yi.reveal<bool>();
            break;
        }


        default:
            std::cerr << "Invalid rule id" << rule_id << std::endl;
    }



    delete table_io;
    delete input_io;
    delete output_io;
}


