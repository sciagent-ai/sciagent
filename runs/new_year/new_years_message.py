#!/usr/bin/env python3
"""
New Year's Message App
A simple application to display a festive New Year's 2026 message
"""

import time
import sys
from datetime import datetime


def print_banner():
    """Print a decorative banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          🎆  HAPPY NEW YEAR 2026!  🎆                    ║
    ║                                                           ║
    ║              ✨ Wishing You Joy ✨                       ║
    ║              🌟 Success & Prosperity 🌟                  ║
    ║              🎊 Throughout the Year 🎊                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    return banner


def print_countdown():
    """Print a simple countdown animation"""
    print("\n🎉 New Year Countdown! 🎉\n")
    for i in range(5, 0, -1):
        print(f"   {i}...", end='\r')
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n   🎊 HAPPY NEW YEAR! 🎊\n")


def print_fireworks():
    """Print ASCII fireworks animation"""
    fireworks = [
        "        *",
        "       ***",
        "      *****",
        "     *******",
        "    *********",
        "   ***********",
    ]
    
    print("\n🎆 Fireworks Display 🎆\n")
    for _ in range(2):
        for frame in fireworks:
            print(frame)
            time.sleep(0.1)
        for frame in reversed(fireworks):
            print(frame)
            time.sleep(0.1)
        print()


def get_new_year_message():
    """Generate a personalized New Year message"""
    current_year = datetime.now().year
    next_year = current_year + 1
    
    messages = [
        f"\n🌟 Welcome to {next_year}! 🌟",
        f"\nMay this year bring you:",
        "  ✨ Happiness and joy in every moment",
        "  💪 Strength to overcome challenges",
        "  🎯 Success in all your endeavors",
        "  ❤️  Love and warmth from those around you",
        "  🚀 New opportunities and adventures",
        "  🌈 Colorful memories to cherish",
        f"\nCheers to an amazing {next_year}! 🥂",
    ]
    
    return "\n".join(messages)


def display_interactive_menu():
    """Display an interactive menu"""
    while True:
        print("\n" + "="*60)
        print("🎊 NEW YEAR'S MESSAGE APP 🎊")
        print("="*60)
        print("\nChoose an option:")
        print("  1. Display New Year Banner")
        print("  2. Show Countdown")
        print("  3. Fireworks Animation")
        print("  4. New Year Message")
        print("  5. Show All")
        print("  6. Exit")
        print("\n" + "="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print(print_banner())
        elif choice == '2':
            print_countdown()
        elif choice == '3':
            print_fireworks()
        elif choice == '4':
            print(get_new_year_message())
        elif choice == '5':
            print(print_banner())
            time.sleep(1)
            print_countdown()
            time.sleep(1)
            print_fireworks()
            time.sleep(1)
            print(get_new_year_message())
        elif choice == '6':
            print("\n🎆 Thank you! Have a wonderful New Year! 🎆\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def main():
    """Main function to run the New Year's message app"""
    print("\n" + "🎊" * 30)
    print("  WELCOME TO THE NEW YEAR'S MESSAGE APP!")
    print("🎊" * 30 + "\n")
    
    try:
        display_interactive_menu()
    except KeyboardInterrupt:
        print("\n\n🎆 Thank you! Have a wonderful New Year! 🎆\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
