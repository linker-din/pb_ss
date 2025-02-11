import math

def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n):
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

def main():
    print("Factorial of 5:", factorial(5))
    print("Is 17 prime?:", is_prime(17))
    print("First 10 Fibonacci numbers:", fibonacci(10))

if __name__ == "__main__":
    main()