#!/usr/bin/env python3
"""
Fibonacci Series Test Script

This script implements and tests different approaches to generate Fibonacci numbers.
"""

import time
import sys

def fibonacci_recursive(n):
    """
    Calculate the nth Fibonacci number using recursion.
    Warning: This is inefficient for large values of n due to repeated calculations.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-indexed)
        
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def fibonacci_iterative(n):
    """
    Calculate the nth Fibonacci number using iteration.
    This is more efficient for large values of n.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-indexed)
        
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

def fibonacci_sequence(n, method="iterative"):
    """
    Generate a list of Fibonacci numbers up to the nth position.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-indexed)
        method (str): The method to use ('recursive' or 'iterative')
        
    Returns:
        list: A list of Fibonacci numbers from F(0) to F(n)
    """
    if method == "recursive":
        return [fibonacci_recursive(i) for i in range(n+1)]
    else:
        sequence = []
        for i in range(n+1):
            sequence.append(fibonacci_iterative(i))
        return sequence

def performance_test(n):
    """
    Compare the performance of recursive and iterative Fibonacci implementations.
    
    Args:
        n (int): The position in the Fibonacci sequence to calculate
    """
    print(f"\nPerformance test for calculating F({n}):")
    
    # Test iterative approach
    start_time = time.time()
    result_iterative = fibonacci_iterative(n)
    iterative_time = time.time() - start_time
    print(f"Iterative approach: {iterative_time:.6f} seconds")
    
    # Test recursive approach (with a limit to prevent very long calculations)
    if n <= 30:  # Limit recursive test to avoid excessive runtime
        start_time = time.time()
        result_recursive = fibonacci_recursive(n)
        recursive_time = time.time() - start_time
        print(f"Recursive approach: {recursive_time:.6f} seconds")
        print(f"Recursive is {recursive_time/iterative_time:.2f}x slower than iterative")
    else:
        print("Recursive approach skipped for n > 30 (would take too long)")
    
    return result_iterative

def main():
    """Main function to run the Fibonacci tests."""
    print("Fibonacci Series Test")
    print("====================")
    
    # Get the number of Fibonacci numbers to generate
    try:
        if len(sys.argv) > 1:
            n = int(sys.argv[1])
        else:
            n = int(input("Enter the number of Fibonacci numbers to generate: "))
        
        if n < 0:
            raise ValueError("Number must be non-negative")
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Display the Fibonacci sequence
    print(f"\nFibonacci Sequence (first {n+1} numbers):")
    sequence = fibonacci_sequence(n)
    for i, num in enumerate(sequence):
        print(f"F({i}) = {num}")
    
    # Run performance test
    test_n = min(n, 35)  # Limit test to avoid excessive runtime
    result = performance_test(test_n)
    print(f"\nF({test_n}) = {result}")
    
    # Show a larger number calculated with the efficient method
    if n < 50:
        large_n = 50
        print(f"\nCalculating a larger Fibonacci number for demonstration:")
        start_time = time.time()
        large_result = fibonacci_iterative(large_n)
        calc_time = time.time() - start_time
        print(f"F({large_n}) = {large_result} (calculated in {calc_time:.6f} seconds)")

if __name__ == "__main__":
    main()