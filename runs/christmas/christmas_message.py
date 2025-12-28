#!/usr/bin/env python3
"""
Christmas Message App
A simple festive application displaying a Christmas message
"""

import time
import sys
from datetime import datetime


def print_christmas_tree():
    """Print a colorful ASCII Christmas tree"""
    tree = """
          ⭐
         🎄🎄🎄
        🎄🎄🎄🎄🎄
       🎄🎄🎄🎄🎄🎄🎄
      🎄🎄🎄🎄🎄🎄🎄🎄🎄
     🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄
          |||
          |||
    """
    return tree


def print_decorative_border(width=60):
    """Print a decorative border"""
    return "🎅" + "=" * (width - 2) + "🎁"


def animate_message(message, delay=0.05):
    """Animate the message character by character"""
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def main():
    """Main function to display Christmas message"""
    # Clear screen (works on Unix/Linux/Mac)
    print("\033[2J\033[H")
    
    # Get current date
    current_date = datetime.now()
    
    # Print decorative header
    border = print_decorative_border()
    print(border)
    print()
    
    # Print Christmas tree
    print(print_christmas_tree())
    print()
    
    # Main Christmas message
    messages = [
        "🎄 ✨ MERRY CHRISTMAS! ✨ 🎄",
        "",
        "May your days be merry and bright,",
        "And may all your Christmases be white! ❄️",
        "",
        "Wishing you joy, peace, and happiness",
        "this holiday season! 🎁",
        "",
        f"Date: {current_date.strftime('%B %d, %Y')}",
        f"Time: {current_date.strftime('%I:%M %p')}",
    ]
    
    # Print messages with animation
    for msg in messages:
        if msg:
            print(" " * ((60 - len(msg)) // 2) + msg)
        else:
            print()
        time.sleep(0.3)
    
    print()
    print(border)
    
    # Additional festive elements
    print("\n🎵 Deck the halls with boughs of holly! 🎵")
    print("🔔 Fa la la la la, la la la la! 🔔\n")
    
    # Interactive element
    try:
        input("\nPress Enter to spread more Christmas cheer... ")
        print("\n✨ Ho Ho Ho! Have a wonderful holiday season! ✨")
        print("🎅 Santa's workshop wishes you all the best! 🎁\n")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye and Happy Holidays! 🎄\n")


if __name__ == "__main__":
    main()
