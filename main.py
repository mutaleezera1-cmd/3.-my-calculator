
# =========================================================
# CAST TIGER UG - SCIENTIFIC CALCULATOR
# Developer: Mutale Ezera
# Contact: mutaleezera7@gmail.com
# Version: 1.0.0
# Built with Python and Kivy
# =========================================================

import ast
import math
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


# ---------- APP COLORS ----------
BACKGROUND = "#101722"
PANEL = "#1D2938"
NUMBER = "#29394D"
SCIENTIFIC = "#344D69"
OPERATOR = "#176B87"
GREEN = "#13835E"
RED = "#B93B4B"
WHITE = "#FFFFFF"
MUTED = "#B9C7D8"

Window.clearcolor = get_color_from_hex(BACKGROUND)


def colour(value):
    return get_color_from_hex(value)


# ---------- MATHEMATICS ENGINE ----------
class MathEngine:

    def __init__(self):
        self.degrees = True
        self.answer = 0

    def functions(self):

        def angle(x):
            return math.radians(x) if self.degrees else x

        def inverse_angle(fn, x):
            result = fn(x)
            return math.degrees(result) if self.degrees else result

        def factorial(x):
            if not isinstance(x, (int, float)):
                raise ValueError("Invalid factorial")
            if x < 0 or x != int(x) or x > 170:
                raise ValueError("Use an integer from 0 to 170")
            return math.factorial(int(x))

        return {
            "sin": lambda x: math.sin(angle(x)),
            "cos": lambda x: math.cos(angle(x)),
            "tan": lambda x: math.tan(angle(x)),
            "asin": lambda x: inverse_angle(math.asin, x),
            "acos": lambda x: inverse_angle(math.acos, x),
            "atan": lambda x: inverse_angle(math.atan, x),
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "abs": abs,
            "exp": math.exp,
            "factorial": factorial,
        }

    def evaluate(self, expression):
        expression = expression.replace("π", "pi")
        expression = expression.replace("^", "**")

        tree = ast.parse(expression, mode="eval")

        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }

        constants = {
            "pi": math.pi,
            "e": math.e,
            "Ans": self.answer,
        }

        funcs = self.functions()

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value
                raise ValueError("Invalid number")

            if isinstance(node, ast.Name):
                if node.id in constants:
                    return constants[node.id]
                raise ValueError("Unknown symbol")

            if isinstance(node, ast.UnaryOp):
                value = visit(node.operand)

                if isinstance(node.op, ast.USub):
                    return -value

                if isinstance(node.op, ast.UAdd):
                    return value

                raise ValueError("Invalid sign")

            if isinstance(node, ast.BinOp):
                op_type = type(node.op)

                if op_type not in operations:
                    raise ValueError("Unsupported operation")

                a = visit(node.left)
                b = visit(node.right)

                if op_type is ast.Pow:
                    if abs(b) > 100:
                        raise ValueError("Exponent too large")
                    if abs(a) > 1e100:
                        raise ValueError("Base too large")

                return operations[op_type](a, b)

            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    raise ValueError("Invalid function")

                name = node.func.id

                if name not in funcs or len(node.args) != 1:
                    raise ValueError("Unknown function")

                return funcs[name](visit(node.args[0]))

            raise ValueError("Invalid expression")

        result = visit(tree)

        if isinstance(result, complex):
            raise ValueError("Complex result not supported")

        if not isinstance(result, (int, float)):
            raise ValueError("Invalid result")

        if not math.isfinite(result):
            raise ValueError("Result is not finite")

        self.answer = result
        return result


# ---------- CALCULATOR APP ----------
class CastTigerCalculator(App):

    def build(self):
        self.title = "CAST TIGER UG"
        self.engine = MathEngine()
        self.history_items = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        # Brand heading
        header = BoxLayout(
            size_hint_y=None,
            height=dp(54),
            spacing=dp(5)
        )

        heading = Label(
            text="CAST TIGER UG",
            font_size="21sp",
            bold=True,
            color=colour(WHITE),
            halign="left"
        )
        header.add_widget(heading)

        self.mode_btn = Button(
            text="DEG",
            size_hint_x=None,
            width=dp(70),
            background_normal="",
            background_color=colour(GREEN)
        )
        self.mode_btn.bind(on_release=self.toggle_mode)
        header.add_widget(self.mode_btn)
        root.add_widget(header)

        # Calculator display
        self.display = TextInput(
            text="",
            hint_text="Enter calculation",
            multiline=False,
            halign="right",
            font_size="30sp",
            size_hint_y=None,
            height=dp(75),
            padding=[dp(8), dp(18)],
            background_color=colour(PANEL),
            foreground_color=colour(WHITE),
            cursor_color=colour(WHITE)
        )
        root.add_widget(self.display)

        self.status = Label(
            text="Scientific Calculator",
            size_hint_y=None,
            height=dp(25),
            font_size="13sp",
            color=colour(MUTED)
        )
        root.add_widget(self.status)

        # Button layout
        rows = [
            ["sin", "cos", "tan", "(", ")"],
            ["asin", "acos", "atan", "sqrt", "x²"],
            ["log", "ln", "exp", "xʸ", "n!"],
            ["7", "8", "9", "÷", "DEL"],
            ["4", "5", "6", "×", "AC"],
            ["1", "2", "3", "−", "Ans"],
            ["0", ".", "π", "+", "e"],
            ["±", "%", "mod", "=", "HIST"],
        ]

        keypad = GridLayout(
            cols=5,
            spacing=dp(5),
            size_hint_y=1
        )

        for row in rows:
            for symbol in row:
                btn = Button(
                    text=symbol,
                    font_size="17sp",
                    background_normal="",
                    background_down="",
                    background_color=colour(
                        self.button_colour(symbol)
                    ),
                    color=colour(WHITE)
                )
                btn.bind(on_release=self.press)
                keypad.add_widget(btn)

        root.add_widget(keypad)

        # Calculation history
        self.history_label = Label(
            text="By Mutale Ezera | Version 1.0.0",
            size_hint_y=None,
            height=dp(42),
            font_size="11sp",
            color=colour(MUTED),
            halign="center",
            valign="middle"
        )
        root.add_widget(self.history_label)

        footer = Label(
            text="Contact: mutaleezera7@gmail.com",
            size_hint_y=None,
            height=dp(22),
            font_size="10sp",
            color=colour(MUTED)
        )
        root.add_widget(footer)

        return root

    def button_colour(self, symbol):

        if symbol == "=":
            return GREEN

        if symbol in ("AC", "DEL"):
            return RED

        if symbol in ("+", "−", "×", "÷", "%", "mod"):
            return OPERATOR

        scientific_buttons = (
            "sin", "cos", "tan", "asin", "acos", "atan",
            "sqrt", "x²", "xʸ", "n!", "log", "ln", "exp",
            "π", "e", "Ans", "HIST"
        )

        if symbol in scientific_buttons:
            return SCIENTIFIC

        return NUMBER

    def toggle_mode(self, instance):
        self.engine.degrees = not self.engine.degrees

        self.mode_btn.text = (
            "DEG" if self.engine.degrees else "RAD"
        )

        self.status.text = (
            "Angles in degrees"
            if self.engine.degrees
            else "Angles in radians"
        )

    def press(self, instance):
        key = instance.text
        current = self.display.text

        try:
            if key == "AC":
                self.display.text = ""
                self.status.text = "Cleared"

            elif key == "DEL":
                self.display.text = current[:-1]

            elif key == "HIST":
                self.history_label.text = (
                    "\n".join(self.history_items[-2:])
                    if self.history_items
                    else "No calculation history"
                )

            elif key == "=":
                if not current.strip():
                    return

                result = self.engine.evaluate(current)

                if isinstance(result, int):
                    answer_text = str(result)
                else:
                    answer_text = f"{result:.12g}"

                self.history_items.append(
                    f"{current} = {answer_text}"
                )

                self.display.text = answer_text
                self.history_label.text = (
                    f"{current} = {answer_text}"
                )
                self.status.text = "Calculation complete"

            elif key == "±":
                if current:
                    self.display.text = f"-({current})"

            elif key == "sqrt":
                self.display.text += "sqrt("

            elif key == "x²":
                self.display.text += "^2"

            elif key == "xʸ":
                self.display.text += "^"

            elif key == "n!":
                self.display.text += "factorial("

            elif key in (
                "sin", "cos", "tan", "asin", "acos",
                "atan", "log", "ln", "exp"
            ):
                self.display.text += key + "("

            elif key == "÷":
                self.display.text += "/"

            elif key == "×":
                self.display.text += "*"

            elif key == "−":
                self.display.text += "-"

            elif key == "π":
                self.display.text += "pi"

            elif key == "mod":
                self.display.text += "%"

            elif key == "%":
                self.display.text += "/100"

            elif key == "Ans":
                self.display.text += "Ans"

            else:
                self.display.text += key

        except ZeroDivisionError:
            self.status.text = "Error: Division by zero"

        except Exception as error:
            self.status.text = "Error: " + str(error)


if __name__ == "__main__":
    CastTigerCalculator().run()


