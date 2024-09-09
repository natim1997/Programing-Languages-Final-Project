import os
import sys

from Interpreter.context import Context
from Interpreter.interpreter import Interpreter
from Lexer.lexer import Lexer
from Interpreter.myfunction import BuiltInFunction
from Interpreter.number import Number
from Parser.parser import Parser
from Interpreter.symboltable import SymbolTable
run_line = False
global_symbol_table = SymbolTable()
global_symbol_table.add("null", Number.null)
global_symbol_table.add("true", Number.true)
global_symbol_table.add("false", Number.false)
global_symbol_table.add("print", BuiltInFunction.print)
global_symbol_table.add("is_number", BuiltInFunction.is_number)
global_symbol_table.add("is_function", BuiltInFunction.is_function)
global_symbol_table.add("clear", BuiltInFunction.clear)
global_symbol_table.add("cls", BuiltInFunction.clear)
global_symbol_table.add("z", Number(3))


def main():
    print("Welcome to our final project in Programming Language")
    print("This is a simple shell for our programming language")
    print("To exit the shell, type 'exit'")
    print("To clear the screen, type 'clear'")

    while True:
        mode = input("Would you like to read from a file or run commands in the console? (file/console): ").strip().lower()

        if mode == "exit":
            print("Exiting...")
            break
        elif mode == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        if mode == "file":
            file_name = input("Enter the file name: ").strip()
            if not os.path.isfile(file_name):
                print("File not found.")
                continue

            run_mode = input("Would you like to run the entire file or line by line? (all/line): ").strip().lower()
            if run_mode == "exit":
                print("Exiting...")
                break
            elif run_mode == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            with open(file_name, 'r') as file:
                file_text = file.readlines()

            if run_mode == "line":
                for line in file_text:
                    result, error = run(file_name, line.strip())
                    if error:
                        print(error.__str__())
                    elif result is not None and not (isinstance(result, Number) and result.value == 0):
                        print(f"The result is: {result}")
                    sys.stdout.flush()

                    user_input = input("Do you want to execute the next line? (yes/no/exit/clear): ").strip().lower()
                    if user_input == "no" or user_input == "exit":
                        print("Stopping execution.")
                        break
                    elif user_input == "clear":
                        os.system('cls' if os.name == 'nt' else 'clear')
            else:
                for line in file_text:
                    result, error = run(file_name, line.strip())
                    if error:
                        print(error.__str__())
                    elif result is not None and not (isinstance(result, Number) and result.value == 0):
                        print(f"The result is: {result}")
                    sys.stdout.flush()

        elif mode == "console":
            while True:
                txt = input("calc> ")
                if txt.strip().lower() == "exit":
                    print("Exiting...")
                    print("Goodbye! see you soon :)")
                    return
                elif txt.strip().lower() == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                result, error = run('<stdin>', txt)
                if error:
                    print(error.__str__())
                elif result is not None:
                    print(f"The result is: {result}")
        else:
            print("Invalid option. Please choose 'file' or 'console'.")

    print("Goodbye! see you soon :)")


def run(file_name, txt):
    global run_line
    # Generate tokens
    lexer_instance = Lexer(file_name, txt)
    tokens, error = lexer_instance.tokenize()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # print(ast.node)

    # Now we can run the program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = None
    if isinstance(ast.node, list):
        for node in ast.node:
            if run_line:
                print("line: ", end="")
                print("result: ", end="")
            result = interpreter.visit(node, context)
            if result.error:
                break
            if run_line:
                if result.value:
                    print(result.value)
                sys.stdout.flush()
                input("Press Enter to continue...")
    else:
        result = interpreter.visit(ast.node, context)
    return result.value, result.error


if __name__ == '__main__':
    main()
