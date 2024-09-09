from functools import reduce
# Q1
fibonacci = lambda n: [0, 1][:n] + [0] * (n-2) if n > 2 else [0, 1][:n]
# Example usage:
n = 10
fib_seq = fibonacci(n)
for i in range(2, n):
    fib_seq[i] = fib_seq[i-1] + fib_seq[i-2]
print(fib_seq)  # Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Q2
concat_strings = lambda strings: reduce(lambda x, y: x + ' ' + y, strings)
# Example usage:
strings = ["Hello", "world", "this", "is", "short"]
result = concat_strings(strings)
print(result)  # Output: "Hello world this is short"

# Q3
def cumulative_sum_of_squares_even(lst):
    return list(map(lambda sublist: reduce(lambda acc, x: (lambda y: y + (lambda z: z**2)(x) if (lambda w: w % 2 == 0)(x) else y)(acc), sublist, 0), lst))
# Example usage:
input_data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
result = cumulative_sum_of_squares_even(input_data)
print(result)

# Q4
# Higher-order function
def right_associative_exponentiation(seq):
    return reduce(lambda x, y: y ** x, reversed(seq))
# Example usage:
exp_result = right_associative_exponentiation([2, 3, 2])
print("Exponentiation result of 2^3^2:", exp_result)

# Q5
sum_squared = reduce(lambda acc, x: acc + x, map(lambda x: x**2, filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5, 6])))
print(sum_squared)

# Q6
count_palindromes = lambda lst: list(map(lambda sublist: reduce(lambda acc, s: acc + 1, filter(lambda x: x == x[::-1], sublist), 0), lst))
input_data = [["madam", "test", "racecar"], ["hello", "level", "world"], ["noon", "python"]]
result = count_palindromes(input_data)
print(result)

# Q7
# Lazy Evaluation is a programming concept where an expression is not evaluated until its value is actually needed.
# This contrasts with Eager Evaluation, where expressions are evaluated as soon as they are encountered.

# Q8
get_primes_desc = lambda lst: sorted([x for x in lst if x > 1 and all(x % i != 0 for i in range(2, int(x**0.5) + 1))], reverse=True)
print(get_primes_desc([10, 11, 4, 7, 13, 17, 20]))
