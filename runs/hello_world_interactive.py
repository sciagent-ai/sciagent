#!/usr/bin/env python3
"""
Interactive Hello World Application
A more interactive version that greets the user by name.
"""

def greet_user(name):
    """Greet the user with a personalized message."""
    print(f"\n👋 Hello, {name}! Welcome to the interactive Hello World app!")
    print(f"Nice to meet you, {name}! 🎉")


def main():
    """Main function to run the interactive hello world app."""
    print("=" * 60)
    print("🌟 Interactive Hello World Application 🌟")
    print("=" * 60)
    
    # Get user input
    name = input("\nWhat's your name? ")
    
    if name.strip():
        greet_user(name.strip())
    else:
        print("\n👋 Hello, Anonymous! Welcome to the Hello World app!")
    
    print("\n" + "=" * 60)
    print("Thank you for using the Hello World app! 😊")
    print("=" * 60)


if __name__ == "__main__":
    main()
