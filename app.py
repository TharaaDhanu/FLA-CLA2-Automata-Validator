from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ============================================================
# TASK 2 - FINITE AUTOMATA
# ============================================================

def atm_pin_trace(value):
    states = ["q0"]
    steps = [{
        "title": "Start",
        "detail": "The DFA starts in q0 and waits for the first decimal digit.",
        "transition": "q0"
    }]

    if not value or not value.isascii() or not value.isdigit():
        return False, states, steps, "Only decimal digits are allowed."

    for i, ch in enumerate(value, 1):
        if i <= 4:
            next_state = f"q{i}"
            states.append(next_state)
            steps.append({
                "title": f"Read digit {i}",
                "detail": f"Read '{ch}'. The DFA moves from q{i-1} to {next_state}. {i} digit(s) processed.",
                "transition": f"q{i-1} → {next_state}"
            })
        else:
            steps.append({
                "title": "Length violation",
                "detail": "A fifth digit was found. The DFA requires exactly four digits.",
                "transition": "q4 → reject"
            })
            return False, states, steps, "PIN must contain exactly four digits."

    if len(value) == 4:
        steps.append({
            "title": "Accept",
            "detail": "The DFA reached q4 after reading exactly four digits. q4 is the accepting state.",
            "transition": "q4 = accepting"
        })
        return True, states, steps, "Exactly four digits. The ATM PIN is accepted."

    steps.append({
        "title": "Incomplete input",
        "detail": f"Only {len(value)} digit(s) were read. The DFA needs exactly four digits.",
        "transition": f"q{len(value)} → reject"
    })
    return False, states, steps, "PIN must contain exactly four digits."


def password_trace(value):
    states = ["q0"]
    steps = [{
        "title": "Start",
        "detail": "The DFA starts in q0 and expects an uppercase English letter first.",
        "transition": "q0"
    }]

    if len(value) != 8:
        steps.append({
            "title": "Length check failed",
            "detail": f"The input contains {len(value)} character(s). Exactly 8 characters are required.",
            "transition": "reject"
        })
        return False, states, steps, "Password must contain exactly 8 characters."

    if not (value[0].isascii() and value[0].isupper()):
        steps.append({
            "title": "First character check failed",
            "detail": f"'{value[0]}' is not an uppercase English letter.",
            "transition": "q0 → reject"
        })
        return False, states, steps, "First character must be uppercase."

    states.append("q1")
    steps.append({
        "title": "Read character 1",
        "detail": f"'{value[0]}' is uppercase, so the DFA moves from q0 to q1.",
        "transition": "q0 → q1"
    })

    for pos in range(1, 7):
        ch = value[pos]
        if not (ch.isascii() and ch.isalnum()):
            steps.append({
                "title": f"Character {pos+1} check failed",
                "detail": f"'{ch}' is not an ASCII letter or digit. Positions 2–7 must be alphanumeric.",
                "transition": f"q{pos} → reject"
            })
            return False, states, steps, f"Character {pos+1} must be alphanumeric."
        states.append(f"q{pos+1}")
        steps.append({
            "title": f"Read character {pos+1}",
            "detail": f"'{ch}' is alphanumeric, so the DFA moves to q{pos+1}.",
            "transition": f"q{pos} → q{pos+1}"
        })

    if not (value[7].isascii() and value[7].isdigit()):
        steps.append({
            "title": "Final character check failed",
            "detail": f"'{value[7]}' is not a digit. The eighth character must be a digit.",
            "transition": "q7 → reject"
        })
        return False, states, steps, "Final character must be a digit."

    states.append("q8")
    steps.append({
        "title": "Accept",
        "detail": f"'{value[7]}' is a digit. The DFA reaches q8, the accepting state.",
        "transition": "q7 → q8 = accepting"
    })
    return True, states, steps, "Password matches the DFA rule."


def email_trace(value):
    states = ["q0"]
    steps = [{
        "title": "Start",
        "detail": "The DFA begins at q0 and expects one or more letters/digits for the local part.",
        "transition": "q0"
    }]

    match = re.fullmatch(r"[A-Za-z0-9]+@[A-Za-z0-9]+\.[a-z]{1,3}", value)
    if not match:
        steps.append({
            "title": "Pattern check failed",
            "detail": "Expected the simplified form local@domain.tld: alphanumeric local part, '@', alphanumeric domain, '.', and a 1–3 letter lowercase TLD.",
            "transition": "reject"
        })
        return False, states, steps, "Expected: local@domain.tld (simplified DFA rule)."

    local, rest = value.split("@", 1)
    domain, tld = rest.rsplit(".", 1)

    for idx, ch in enumerate(local, 1):
        states.append("q1")
        steps.append({
            "title": f"Read local-part character {idx}",
            "detail": f"'{ch}' is an allowed local-part symbol, so the DFA stays in q1.",
            "transition": "q1 → q1"
        })

    states.append("q2")
    steps.append({
        "title": "Read @",
        "detail": "The '@' separator is found. The DFA moves from q1 to q2.",
        "transition": "q1 → q2"
    })

    for idx, ch in enumerate(domain, 1):
        states.append("q3")
        steps.append({
            "title": f"Read domain character {idx}",
            "detail": f"'{ch}' is an allowed domain symbol, so the DFA stays in q3.",
            "transition": "q3 → q3"
        })

    states.append("q4")
    steps.append({
        "title": "Read dot",
        "detail": "The '.' separator before the top-level domain is read.",
        "transition": "q3 → q4"
    })

    states.append("q5")
    steps.append({
        "title": "Read TLD",
        "detail": f"'{tld}' satisfies the simplified 1–3 lowercase-letter TLD rule.",
        "transition": "q4 → q5"
    })

    steps.append({
        "title": "Accept",
        "detail": "The complete string matches the simplified e-mail DFA.",
        "transition": "q5 = accepting"
    })
    return True, states, steps, "E-mail matches the simplified DFA rule."


# ============================================================
# TASK 3 - PDA / CFG CASE STUDIES
# ============================================================

def balanced_trace(value):
    stack = ["Z0"]
    steps = [{
        "title": "Start stack",
        "detail": "The PDA starts with bottom-of-stack marker Z0.",
        "transition": "Stack = [Z0]"
    }]
    pairs = {")": "(", "]": "[", "}": "{"}

    for pos, ch in enumerate(value, 1):
        if ch in "([{":
            stack.append(ch)
            steps.append({
                "title": f"Symbol {pos}: '{ch}'",
                "detail": f"Opening bracket is pushed onto the stack. The top is now '{ch}'.",
                "transition": f"PUSH {ch}"
            })
        elif ch in pairs:
            expected = pairs[ch]
            if len(stack) == 1 or stack[-1] != expected:
                steps.append({
                    "title": f"Mismatch at symbol {pos}",
                    "detail": f"Read '{ch}', but the stack top is {stack[-1] if len(stack) > 1 else 'Z0'}. Expected '{expected}'.",
                    "transition": "reject"
                })
                return False, steps, stack, f"Mismatch at position {pos}: {ch}"
            stack.pop()
            steps.append({
                "title": f"Symbol {pos}: '{ch}'",
                "detail": f"Closing bracket matches the stack top '{expected}', so it is popped.",
                "transition": f"POP {expected}"
            })
        else:
            steps.append({
                "title": f"Invalid symbol at {pos}",
                "detail": f"'{ch}' is not one of (, ), [, ], {{, }}.",
                "transition": "reject"
            })
            return False, steps, stack, f"Invalid symbol: {ch}"

    if len(stack) == 1:
        steps.append({
            "title": "Accept",
            "detail": "All opening brackets were matched and the stack returned to Z0.",
            "transition": "Stack = [Z0] → accepting"
        })
        return True, steps, stack, "Balanced brackets accepted."

    steps.append({
        "title": "Unclosed bracket",
        "detail": "The input ended while an opening bracket remained on the stack.",
        "transition": "reject"
    })
    return False, steps, stack, "Unclosed opening bracket remains."


def expression_validate(value):
    compact = value.replace(" ", "")
    tokens = re.findall(r"id|[()+*]", compact)

    if "".join(tokens) != compact or not tokens:
        return False, [{
            "title": "Lexical check failed",
            "detail": "Only id, +, *, (, and ) are allowed.",
            "transition": "reject"
        }], "Expression violates the grammar.", "CFG + recursive-descent parser"

    i = 0
    steps = []

    def E():
        nonlocal i
        steps.append({"title": "Apply E → T", "detail": "An expression starts by parsing a term.", "transition": "E → T"})
        if not T():
            return False
        while i < len(tokens) and tokens[i] == "+":
            steps.append({"title": "Read +", "detail": "The parser sees '+', so another term is required.", "transition": "E → E + T"})
            i += 1
            if not T():
                return False
        return True

    def T():
        nonlocal i
        steps.append({"title": "Apply T → F", "detail": "A term starts by parsing a factor.", "transition": "T → F"})
        if not F():
            return False
        while i < len(tokens) and tokens[i] == "*":
            steps.append({"title": "Read *", "detail": "The parser sees '*', so another factor is required.", "transition": "T → T * F"})
            i += 1
            if not F():
                return False
        return True

    def F():
        nonlocal i
        if i < len(tokens) and tokens[i] == "id":
            steps.append({"title": "Read id", "detail": "The identifier is a valid factor.", "transition": "F → id"})
            i += 1
            return True
        if i < len(tokens) and tokens[i] == "(":
            steps.append({"title": "Read (", "detail": "An opening parenthesis begins a nested expression.", "transition": "F → (E)"})
            i += 1
            if not E():
                return False
            if i >= len(tokens) or tokens[i] != ")":
                steps.append({"title": "Missing )", "detail": "The nested expression was not closed with ')'.", "transition": "reject"})
                return False
            steps.append({"title": "Read )", "detail": "The nested expression is closed successfully.", "transition": "match )"})
            i += 1
            return True
        steps.append({
            "title": "Expected factor",
            "detail": "Expected id or '(' at the current position.",
            "transition": "reject"
        })
        return False

    ok = E() and i == len(tokens)
    if ok:
        steps.append({
            "title": "Accept",
            "detail": "All tokens were consumed and the string satisfies E → E+T, T → T*F, F → (E) | id.",
            "transition": "accept"
        })
        return True, steps, "Expression is valid under the given CFG.", "CFG + recursive-descent parser"

    if i < len(tokens):
        steps.append({
            "title": "Extra token",
            "detail": f"Token '{tokens[i]}' remains after parsing the expression.",
            "transition": "reject"
        })
    return False, steps, "Expression violates the grammar.", "CFG + recursive-descent parser"


def wcwr(value):
    parts = value.split("c")
    steps = [{
        "title": "Find center marker",
        "detail": "The language is w c wᴿ, so exactly one center marker c is required.",
        "transition": "split at c"
    }]

    if len(parts) != 2:
        steps.append({
            "title": "Center check failed",
            "detail": "The input must contain exactly one c.",
            "transition": "reject"
        })
        return False, steps, "Exactly one center marker c is required.", "DPDA"

    left, right = parts
    steps.append({
        "title": "Read left half",
        "detail": f"w = '{left}'. The PDA conceptually pushes the symbols of w before reaching c.",
        "transition": f"PUSH {left or 'ε'}"
    })
    steps.append({
        "title": "Read center",
        "detail": "The PDA reads c and switches from pushing to matching mode.",
        "transition": "read c"
    })
    steps.append({
        "title": "Match right half",
        "detail": f"wᴿ should be '{left[::-1]}'. The supplied right half is '{right}'.",
        "transition": f"POP against {right or 'ε'}"
    })

    if left == right[::-1]:
        steps.append({
            "title": "Accept",
            "detail": "The right side is exactly the reverse of the left side.",
            "transition": "accept"
        })
        return True, steps, "w equals reverse(w); the string is accepted.", "DPDA"

    steps.append({
        "title": "Reject",
        "detail": "The right side is not the reverse of the left side.",
        "transition": "reject"
    })
    return False, steps, "Right side is not reverse(w).", "DPDA"


def wwr(value):
    steps = [{
        "title": "Start",
        "detail": "The language is wwᴿ over alphabet {a,b}. The midpoint is not marked, so an NPDA can guess it.",
        "transition": "start"
    }]

    if any(ch not in "ab" for ch in value):
        steps.append({
            "title": "Alphabet check failed",
            "detail": "Only a and b are permitted.",
            "transition": "reject"
        })
        return False, steps, "Alphabet must be {a,b}.", "NPDA"

    n = len(value)
    if n % 2:
        steps.append({
            "title": "Length check failed",
            "detail": f"The input length is {n}, which is odd. wwᴿ always has even length.",
            "transition": "reject"
        })
        return False, steps, "wwᴿ must have even length.", "NPDA"

    left, right = value[:n//2], value[n//2:]
    steps.append({
        "title": "Guess midpoint",
        "detail": f"The NPDA guesses the midpoint after '{left}'.",
        "transition": f"w = {left}"
    })
    steps.append({
        "title": "Reverse-match",
        "detail": f"The second half is '{right}', while reverse(w) is '{left[::-1]}'.",
        "transition": f"compare {right} with {left[::-1]}"
    })

    if left == right[::-1]:
        steps.append({
            "title": "Accept",
            "detail": "The second half is exactly the reverse of the first half.",
            "transition": "accept"
        })
        return True, steps, "Second half is reverse of first half.", "NPDA"

    steps.append({
        "title": "Reject",
        "detail": "The second half is not the reverse of the first half.",
        "transition": "reject"
    })
    return False, steps, "Second half is not reverse of first half.", "NPDA"


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/validate")
def validate():
    data = request.get_json(silent=True) or request.form
    task = data.get("task", "")
    value = data.get("value", "")

    if task == "atm":
        ok, states, steps, msg = atm_pin_trace(value)
        return jsonify(ok=ok, message=msg, states=states, steps=steps,
                       model="DFA", value=value, task="task2",
                       diagram="atm")

    if task == "password":
        ok, states, steps, msg = password_trace(value)
        return jsonify(ok=ok, message=msg, states=states, steps=steps,
                       model="DFA", value=value, task="task2",
                       diagram="password")

    if task == "email":
        ok, states, steps, msg = email_trace(value)
        return jsonify(ok=ok, message=msg, states=states, steps=steps,
                       model="DFA", value=value, task="task2",
                       diagram="email")

    if task == "brackets":
        ok, steps, stack, msg = balanced_trace(value)
        return jsonify(ok=ok, message=msg, steps=steps, stack=stack,
                       model="DPDA", value=value, task="task3",
                       diagram="brackets")

    if task == "expression":
        ok, steps, msg, model = expression_validate(value)
        return jsonify(ok=ok, message=msg, steps=steps,
                       model=model, value=value, task="task3",
                       diagram="expression")

    if task == "wcwr":
        ok, steps, msg, model = wcwr(value)
        return jsonify(ok=ok, message=msg, steps=steps,
                       model=model, value=value, task="task3",
                       diagram="wcwr")

    if task == "wwr":
        ok, steps, msg, model = wwr(value)
        return jsonify(ok=ok, message=msg, steps=steps,
                       model=model, value=value, task="task3",
                       diagram="wwr")

    return jsonify(ok=False, message="Unknown validator.", model="", task="",
                   diagram="")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
