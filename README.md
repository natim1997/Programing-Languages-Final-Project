# Final project - Programing Languages
# Introduction
This project is an interpreter for a concise and functional programming language designed with a focus on immutability and pure functions. This minimalist language promotes problem-solving through recursion, function definitions, and lambda expressions, while deliberately omitting variable assignments to enforce a purely functional approach.
# Authors
- Daniel Jerbi
- Netanel Michel

Inspired by the Make YOUR OWN Programming Language series by CodePulse, this project embodies the principles of functional programming in a minimalist interpreter.
# Data Types
- INTEGER: Supports whole numbers, both positive and negative, including zero. Examples: -7, 0, 19.
- BOOLEAN: Represents logical truth values, True and False.
# Operations
**Arithmetic Operations (Applicable to INTEGERs)**
- Addition (+)
- Subtraction (-)
- Multiplication (*)
- Division (/)
- Modulo (%)

**Logical Operations**
- AND (&&)
- OR (||)
- NOT (!)

**Comparison Operations**
- Equal to (==)
- Not equal to (!=)
- Greater than (>)
- Less than (<)
- Greater than or equal to (>=)
- Less than or equal to (<=)
# Functions
**Named Functions**
- Define reusable functions that can be invoked by name.
**Anonymous Functions**
- Create inline, unnamed functions using lambda expressions.
**Function Application**
- Apply functions to arguments to compute and return results.
**Recursion**
- Enable recursion to perform repeated tasks, serving as a substitute for loops.
# Control Structures
**Recursion as Loop Substitute**
- This language avoids traditional looping constructs in favor of recursion, ensuring that all operations align with the language's immutable nature.
# Immutability
- Immutable Values: All values are immutable, meaning that once they are defined, they cannot be altered. This guarantees a consistent functional programming paradigm, free from state mutations and variable reassignments.
# Error Handling
- Syntax Errors: Detects and reports errors related to the incorrect structure or grammar of the code.
- Type Errors: Identifies and flags operations that involve incompatible data types.
- Runtime Errors: Catches and handles errors that occur during the execution of code.
# How to Use
**Installation**
- Clone the repository:
```bash
git clone https://github.com/your-repository/interpreter.git
```
- Navigate to the project directory:
```bash
cd interpreter
```
# Running the Interpreter
You can execute the interpreter in either interactive mode or by running a full script. The interpreter supports both approaches, providing flexibility depending on your needs.
**Interactive Mode**
Launch the interpreter without any arguments to start coding directly in the terminal:
```bash
python shell.py
```
**Script Mode**

To run a complete script, provide the script file as an argument:
```bash
python shell.py test.lambda
```
**Line-by-Line Execution**

For step-by-step execution, use the -l flag:
```bash
python shell.py -l test.lambda
```
# Features
- Support for Named and Anonymous Functions: Define and use both named and lambda functions effortlessly.
- Complete Recursion Support: Replace traditional loops with recursive functions, adhering to the immutable principles.
- Error Handling: Comprehensive error detection for syntax, type, and runtime issues, ensuring robust and error-free code execution.
#Example
An example script (test.lambda) is provided to demonstrate the capabilities of the interpreter. Simply run it using the commands above to see the interpreter in action.

# The BNF Grammar:

```
<statements> ::= newline* <statement>  (newline+ <statement>)* newline*

<statement> ::= continue | break |<parse_boolean_expression> | return

<parse_boolean_expression> ::= <parse_boolean_term> (<and_or_op> <parse_boolean_term>)*

<parse_boolean_term> ::= <parse_boolean_factor> (<equal_op> <parse_boolean_factor>)*

<parse_boolean_factor> ::= <compare_expression> | <boolean> | <not> <parse_boolean_factor>

<compare_expression> ::= <parse_expression> (<compare_op> <parse_expression>)*

<parse_expression> ::= <parse_term> (<add_sub_op> <parse_term>)*

<parse_term> ::= <parse_factor> (<mul_div_op> <parse_factor>)*

<parse_factor> ::= <add_sub_op> <parse_expression> | <call_expression>

<call_expression> ::= <atom> | <atom> "(" <parse_expression> ")"

<atom> ::= <while_expression> | <int> | (<parse_boolean_expression>) | <function_definition> | <identifier> | <def_lambda>

<function_definition> ::= "function" <identifier> "(" <identifier> ("," <identifier>)* ")"  <parse_boolean_expression> "" | "function" "(" <identifier> ("," <identifier>)* ")"  <parse_boolean_expression>

<while_expression> ::= "while" "(" <parse_boolean_expression> ")" "{" <parse_boolean_expression> "}" | "while" "(" <parse_boolean_expression> ")" { newline <statements>}

<def_lambda> ::= "lambda" <identifier> "(" <identifier> ("," <identifier>)* ")" <parse_boolean_expression>

<not> ::= "!"
<boolean> ::= "true" | "false"
<add_sub_op> ::= "+" | "-"
<mul_div_idiv_mod_op> ::= "*" | "/" | "//" | "%"
<and_or_op> ::= "&&" | "||"
<equal_op> ::= "==" | "!="
<compare_op> ::= <equal_op> | ">" | "<" | ">=" | "<="
<int> ::= <regular_numbers> | 0 | <regular_numbers> <int>
<regular_numbers> ::= [1-9]+
<keywords> ::= "while"
<identifier> ::= <letter> (<letter> | <digit>)*

```
