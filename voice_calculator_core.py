"""
Voice Command Calculator
------------------------
Say things like:
  "5 plus 3"
  "twenty five times four"
  "square root of 144"
  "10 percent of 200"
  "2 to the power of 8"
  "answer divided by 2"   (uses the previous result)
  "quit" / "exit"         (stop)

Install:
  pip install SpeechRecognition pyaudio pyttsx3

Run:
  python voice_calculator.py          # voice mode
  python voice_calculator.py --text   # type the commands instead (no mic needed)
"""

import ast
import math
import operator
import re
import sys

# ---------- Optional text-to-speech ----------
try:
    import pyttsx3
    _tts = pyttsx3.init()
except Exception:
    _tts = None


def speak(text: str) -> None:
    print(f"🤖 {text}")
    if _tts:
        _tts.say(text)
        _tts.runAndWait()


# ---------- Number words -> digits ----------
UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALES = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}


def words_to_numbers(text: str) -> str:
    tokens = text.split()
    out, total, current, active, i = [], 0, 0, False, 0

    def flush():
        nonlocal total, current, active
        out.append(str(total + current))
        total = current = 0
        active = False

    while i < len(tokens):
        t = tokens[i]
        if t in UNITS:
            current += UNITS[t]
            active = True
        elif t in TENS:
            current += TENS[t]
            active = True
        elif t == "hundred" and active:
            current = (current or 1) * 100
        elif t in SCALES and active:
            total += (current or 1) * SCALES[t]
            current = 0
        elif t == "point" and active:
            digits = ""
            while i + 1 < len(tokens) and UNITS.get(tokens[i + 1], 10) < 10:
                digits += str(UNITS[tokens[i + 1]])
                i += 1
            value = str(total + current) + ("." + digits if digits else "")
            out.append(value)
            total = current = 0
            active = False
        else:
            if active:
                flush()
            out.append(t)
        i += 1
    if active:
        flush()
    return " ".join(out)


# ---------- Spoken phrase -> math expression ----------
NUM = r"(\d+(?:\.\d+)?)"


def normalize(spoken: str, last_answer=None) -> str:
    s = spoken.lower().strip()
    s = re.sub(r"[?,!]", "", s)
    s = re.sub(r"\b(what is|what's|calculate|compute|equals?|please|tell me)\b", "", s)
    s = words_to_numbers(s)

    # Use the previous result
    if last_answer is not None:
        s = re.sub(r"\b(answer|ans|previous|result|that)\b", str(last_answer), s)

    # Special forms (need numbers, so handle before operator swaps)
    s = re.sub(rf"square root of {NUM}", r"sqrt(\1)", s)
    s = re.sub(rf"{NUM} squared", r"(\1**2)", s)
    s = re.sub(rf"{NUM} cubed", r"(\1**3)", s)
    s = re.sub(rf"{NUM} (?:percent|per cent|%) of {NUM}", r"(\1/100*\2)", s)

    # Operators
    replacements = [
        (r"\b(to the power of|raised to|power)\b", "**"),
        (r"\b(multiplied by|times|into|x)\b", "*"),
        (r"\b(divided by|over)\b", "/"),
        (r"\b(modulo|mod)\b", "%"),
        (r"\b(plus|add|and)\b", "+"),
        (r"\b(minus|subtract|less)\b", "-"),
        (r"\b(open bracket|open parenthesis)\b", "("),
        (r"\b(close bracket|close parenthesis)\b", ")"),
    ]
    for pattern, symbol in replacements:
        s = re.sub(pattern, f" {symbol} ", s)

    return re.sub(r"\s+", " ", s).strip()


# ---------- Safe evaluator (no eval!) ----------
BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")
        return BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
        return UNARY_OPS[type(node.op)](_eval(node.operand))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "sqrt" and len(node.args) == 1):
        return math.sqrt(_eval(node.args[0]))
    raise ValueError("Unsupported expression")


def calculate(expression: str):
    if not re.fullmatch(r"[\d\s+\-*/().%]*(sqrt\([\d\s+\-*/().%]*\)[\d\s+\-*/().%]*)*", expression):
        raise ValueError("I couldn't understand that as math")
    return _eval(ast.parse(expression, mode="eval"))


def format_result(value) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, float):
        value = round(value, 10)
    return str(value)
