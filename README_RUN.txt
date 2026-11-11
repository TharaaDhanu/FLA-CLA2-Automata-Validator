FLA CLA-2 Chrome Web Application
================================

This project implements:
TASK 2
- ATM PIN DFA
- Password DFA
- Simplified E-mail DFA

TASK 3
- Balanced Brackets DPDA-style stack validator
- Arithmetic Expression CFG + recursive-descent parser
- wcw^R DPDA case study
- ww^R NPDA case study

IMPORTANT UI FIX
----------------
Task 2 and Task 3 now have SEPARATE result panels.
A Task 2 result will never remain visible inside Task 3.
Each result contains:
1. Acceptance/rejection
2. Execution trace
3. Automaton/grammar diagram
4. Step-by-step explanation
5. Formal description

RUN IN VS CODE
--------------
1. Extract the ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal.
4. Run:

   python -m pip install -r requirements.txt

5. Run:

   python app.py

6. Open Chrome and visit:

   http://127.0.0.1:5000/

Do not close the terminal while using the web application.

EXAMPLE INPUTS
--------------
Task 2:
ATM PIN       -> 4821
Password      -> Abc123x7
E-mail        -> student@srm.edu

Task 3:
Brackets      -> {[()()]}
Expression    -> id+id*id
wcw^R         -> abccba
ww^R          -> abba

NOTE
----
The e-mail validator is intentionally simplified for the Formal Language
and Automata assignment. It is not a complete real-world e-mail validator.
