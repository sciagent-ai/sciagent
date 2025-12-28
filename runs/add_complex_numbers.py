# This script adds two complex numbers and prints the result

def add_complex_numbers(a, b):
    return a + b

if __name__ == "__main__":
    # Example complex numbers
    num1 = complex(2, 3)  # 2 + 3j
    num2 = complex(4, 5)  # 4 + 5j
    
    result = add_complex_numbers(num1, num2)
    print(f"The sum of {num1} and {num2} is {result}")
