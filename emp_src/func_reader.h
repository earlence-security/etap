#ifndef EXAMPLE_RULES__FUNC_READER_H
#define EXAMPLE_RULES__FUNC_READER_H

#include <fstream>
#include <utility>
#include <variant>
#include <new>
#include <iostream>

#include <emp-tool/emp-tool.h>

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


std::variant<Bit, Integer, String> get_variable(
    const std::vector<std::variant<Bit, Integer, String>>& x,
    const std::vector<std::variant<Bit, Integer, String>>& c,
    const std::vector<std::variant<Bit, Integer, String>>& y, const std::string& s) {

    int idx = std::stoi(s.substr(1));

    if (s[0] == 'x') {
        return x[idx];
    } else if (s[0] == 'c') {
        return c[idx];
    } else if (s[0] == 'i') {
        return y[idx];
    }

}


void execute(const std::string& filename, bool print_output_format = false) {
    std::vector<std::variant<Bit, Integer, String>> x;
    std::vector<std::variant<Bit, Integer, String>> c;
    std::vector<std::variant<Bit, Integer, String>> y;


    std::ifstream infile(filename);
    std::string line;
    while (std::getline(infile, line))
    {
        std::istringstream iss(line);

        std::string var;
        iss >> var;

        // input variable
        if (var[0] == 'x') {
            std::string type;
            iss >> type;
            if (type == "bool") {
                x.emplace_back(std::in_place_type<Bit>, false, ALICE);
            } else if (type == "int") {
                x.emplace_back(std::in_place_type<Integer>, 32, 0, ALICE);
            } else if (type == "str") {
                int length;
                iss >> length;
                x.emplace_back(get_empty_string_labels(length));
            }
        }
            // constant variable
        else if (var[0] == 'c') {
            std::string type;
            iss >> type;
            if (type == "bool") {
                bool value;
                iss >> value;
                c.emplace_back(std::in_place_type<Bit>, value, PUBLIC);
            } else if (type == "int") {
                int value;
                iss >> value;
                c.emplace_back(std::in_place_type<Integer>, 32, value, PUBLIC);
            } else if (type == "str") {
                std::string value;
                std::getline(iss, value);

                for (int i = 0; i < value.length(); i++) {
                    if (value[i] != ' ') {
                        value = value.substr(i);
                        break;
                    }
                }

                std::ofstream ofs("/tmp/tmp.txt");
                ofs<<value<<endl;
                ofs.close();

                c.emplace_back(get_string_labels(value));
            }
        }
            // intermediate variable
        else if (var[0] == 'i') {
            std::string op;
            iss >> op;

            std::variant<Bit, Integer, String> res;
            // bool operation
            if (op == "or") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Bit>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Bit>(get_variable(x, c, y, arg2));
                res = v1 | v2;
            }
            else if (op == "and") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Bit>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Bit>(get_variable(x, c, y, arg2));
                res = v1 & v2;
            }
            else if (op == "not") {
                std::string arg1;
                iss >> arg1;
                auto v1 = std::get<Bit>(get_variable(x, c, y, arg1));
                res = !v1;
            }
                // int operation
            else if (op == ">") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 > v2;
            }
            else if (op == "<") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 < v2;
            }
            else if (op == "+") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 + v2;
            }
            else if (op == "-") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 - v2;
            }
            else if (op == "*") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 * v2;
            }
            else if (op == "/") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<Integer>(get_variable(x, c, y, arg1));
                auto v2 = std::get<Integer>(get_variable(x, c, y, arg2));
                res = v1 / v2;
            }
                // string operation
            else if (op == "eq" || op == "start_with") {
                std::string arg1, arg2;
                iss >> arg1 >> arg2;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));
                auto v2 = std::get<String>(get_variable(x, c, y, arg2));
                res = start_with(v1, v2);
            }
            else if (op == "end_with" || op == "contain") {
                std::string arg1, dfa_file;
                iss >> arg1 >> dfa_file;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));
                res = dfa_match(dfa_file, v1);
            }
            else if (op == "remove") {
                std::string arg1, dfa_file1, dfa_file2;
                iss >> arg1 >> dfa_file1 >> dfa_file2;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));
                res = dfa_remove(dfa_file1, dfa_file2, v1);
            }
            else if (op == "remove_single") {
                std::string arg1, dfa_file;
                iss >> arg1 >> dfa_file;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));
                res = dfa_remove_single_char(dfa_file, v1);
            }
            else if (op == "split") {
                std::string arg1, dfa_file;
                int idx;
                iss >> arg1 >> idx >> dfa_file;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));
                res = split(dfa_file, v1, idx);
            }
            else if (op == "lookup") {
                std::string arg1;
                iss >> arg1;
                auto v1 = std::get<String>(get_variable(x, c, y, arg1));

                int klen, vlen;
                iss >> klen >> vlen;
                std::vector<String> keys;
                std::vector<String> values;
                std::string k;
                std::string v;
                while (iss >> k >> v) {
                    keys.emplace_back(get_string_labels(k, klen));
                    values.emplace_back(get_string_labels(v, vlen));
                }
                res = lookup(v1, keys, values);
            }

            y.push_back(res);
        }
            // reveal output variable
        else if (var[0] == 'p' || var[0] == 'y') {
            std::string arg;
            iss >> arg;
            auto v = get_variable(x, c, y, arg);
            auto type = v.index();
            if (type == 0) {
                std::get<0>(v).reveal();
                if (var[0] == 'y' && print_output_format) {
                    std::cout << var << " bool" << std::endl;
                }
            } else if (type == 1) {
                std::get<1>(v).reveal<int>();
                if (var[0] == 'y' && print_output_format) {
                    std::cout << var << " int" << std::endl;
                }
            } else if (type == 2) {
                for (const auto& b : std::get<2>(v)) {
                    b.reveal<>();
                }
                if (var[0] == 'y' && print_output_format) {
                    std::cout << var << " str " << std::get<2>(v).size()/8 << std::endl;
                }
            }
        }



    }

}



#endif //EXAMPLE_RULES__FUNC_READER_H
