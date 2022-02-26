import dk.brics.automaton.*;
import com.vladsch.ReverseRegEx.util.RegExPattern;
import com.vladsch.ReverseRegEx.util.ReversePattern;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;


public class ExampleRuleDFA {

    static int getStateNumber(State s) {
        return Integer.parseInt( s.toString().split(" ")[1] );
    }

    static int getStateNumber(State s, State initial) {
        if (s == null) {
            return getStateNumber(initial, initial);
        } else {
            return Integer.parseInt( s.toString().split(" ")[1] );
        }
    }

    static String reverseRegex(String regex) {
        ReversePattern rp = ReversePattern.compile(regex);
        return rp.pattern();
    }


    static void printDFA(Automaton a) {
        System.out.println(a.getNumberOfStates());
        System.out.println(getStateNumber(a.getInitialState()));

        for (var state: a.getStates()) {

            String s = String.valueOf(getStateNumber(state)) + ' ' +
                    getStateNumber(state.step('0')) + ' ' +
                    getStateNumber(state.step('1')) + ' ' +
                    (state.isAccept() ? "1" : "0");

            System.out.println(s);
        }
    }

    static String toBitString(String s) {
        byte[] bytes = s.getBytes();
        StringBuilder binary = new StringBuilder();
        for (byte b : bytes)
        {
            int val = b;
            for (int i = 0; i < 8; i++)
            {
                binary.append((val & 128) == 0 ? 0 : 1);
                val <<= 1;
            }
        }
        return binary.toString();
    }


    static String anychars = "((0|1){8})*";
    static String padchars = "(0{8})*";

    static RegExp containsRegex(String p) {
        return new RegExp(anychars + p + anychars);
    }

    static RegExp startsWithRegex(String p) {
        return new RegExp(anychars + p + anychars);
    }

    static RegExp endsWithRegex(String p) {
        return new RegExp(anychars + p + padchars);
    }

    static RegExp matchesRegex(String p) {
        return new RegExp(p + padchars);
    }

    static RegExp findsRegex(String p) {
        return new RegExp(anychars + p);
    }

    static String phonePattern() {
        List<String> ascii_num = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            ascii_num.add( toBitString(String.valueOf(i)) );
        }

        String p = "(" + String.join("|", ascii_num) + "){10}";
        return p;
    }

    public static void main(String[] args) {

        int rule = Integer.parseInt(args[0]);

        String p = null, p2;
        RegExp r;
        RegExp rr = null;
        RegExp r2 = null;
        RegExp rr2 = null;

        switch (rule) {
            case 1:
                p = toBitString("@");
                r = startsWithRegex(p);
                break;

            case 8:
                p = toBitString("http");
                r = containsRegex(p);
                break;

            case 9:
                r = findsRegex(phonePattern());
                rr = findsRegex(reverseRegex(phonePattern()));
                break;

            case 10:
                p = "(" + toBitString("mp4") + "|" + toBitString("avi") + "|" + toBitString("mov") + ")";
                r = endsWithRegex(p);
                break;

            case 5:
                p = toBitString(" ");
                r = findsRegex(p);
                break;


            case 7:
                p = toBitString("$request");
                r = startsWithRegex(p);

                r2 = findsRegex(p);
                rr2 = findsRegex(reverseRegex(p));
                break;

            default:
                throw new IllegalStateException("Unexpected value: " + rule);
        }


        Automaton a = r.toAutomaton();
        printDFA(a);

        if (rr != null) {
            Automaton ra = rr.toAutomaton();
            printDFA(ra);
        }

        if (r2 != null) {
            Automaton a2 = r2.toAutomaton();
            printDFA(a2);
        }

        if (rr2 != null) {
            Automaton ra2 = rr2.toAutomaton();
            printDFA(ra2);
        }


//        String prefix = "((0|1){8})*";
//        String p = "01100001(01100010)+01100011";
//        String rp = reverseRegex(p);
//
//        RegExp r = new RegExp(prefix + p);
//        Automaton a = r.toAutomaton();
//
//        printDFA(a);
//
//        System.out.println(prefix + rp);
//        RegExp rr = new RegExp(prefix + rp);
//        Automaton ra = rr.toAutomaton();
//
//        printDFA(ra);


    }

}
