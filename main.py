import time
import random

def generate_random_numbers(n, start=1, end=100):
    return [random.randint(start, end) for _ in range(n)]

def print_numbers(numbers):
    for num in numbers:
        print(f"Number: {num}")
        time.sleep(0.1)

def main():
    numbers = generate_random_numbers(50, 1, 500)
    print_numbers(numbers)

if __name__ == "__main__":
    main()