#!/usr/bin/env python3
"""
Simple Diwali Celebration App
Displays festive greetings, diya animations, and Diwali wishes
"""

import time
import sys
import random
from datetime import datetime


class DiwaliApp:
    """A simple interactive Diwali celebration application"""
    
    # ANSI color codes for terminal
    COLORS = {
        'red': '\033[91m',
        'yellow': '\033[93m',
        'orange': '\033[38;5;208m',
        'gold': '\033[38;5;220m',
        'bright_yellow': '\033[38;5;226m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
    }
    
    def __init__(self):
        self.running = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        print("\033[2J\033[H", end='')
    
    def print_colored(self, text, color='white', bold=False):
        """Print colored text"""
        color_code = self.COLORS.get(color, self.COLORS['white'])
        bold_code = self.COLORS['bold'] if bold else ''
        print(f"{bold_code}{color_code}{text}{self.COLORS['reset']}")
    
    def print_diya(self, color='yellow'):
        """Print a decorative diya (lamp)"""
        diya = [
            "        ✨",
            "       🔥",
            "      /|\\",
            "     / | \\",
            "    /  |  \\",
            "   (  🪔  )",
            "    \\___/"
        ]
        for line in diya:
            self.print_colored(line, color, bold=True)
            time.sleep(0.1)
    
    def print_rangoli(self):
        """Print a colorful rangoli pattern"""
        rangoli = [
            "           ✦",
            "          ✦ ✦",
            "         ✦ ❋ ✦",
            "        ✦ ❋ ❋ ✦",
            "       ✦ ❋ ✺ ❋ ✦",
            "      ✦ ❋ ✺ ✺ ❋ ✦",
            "     ✦ ❋ ✺ ❈ ✺ ❋ ✦",
            "      ✦ ❋ ✺ ✺ ❋ ✦",
            "       ✦ ❋ ✺ ❋ ✦",
            "        ✦ ❋ ❋ ✦",
            "         ✦ ❋ ✦",
            "          ✦ ✦",
            "           ✦"
        ]
        colors = ['red', 'yellow', 'orange', 'magenta', 'cyan']
        for i, line in enumerate(rangoli):
            self.print_colored(line, colors[i % len(colors)], bold=True)
            time.sleep(0.1)
    
    def print_banner(self):
        """Print the main Diwali banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ✨  🪔  ✨  HAPPY DIWALI  ✨  🪔  ✨                  ║
║                                                           ║
║        Festival of Lights & Prosperity                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.print_colored(banner, 'gold', bold=True)
    
    def print_fireworks(self):
        """Simulate fireworks animation"""
        fireworks = ['✦', '✧', '★', '✨', '💫', '🎆', '🎇']
        positions = [(10, 5), (30, 8), (50, 3), (20, 10), (40, 6)]
        
        for _ in range(3):
            self.clear_screen()
            print("\n" * 2)
            self.print_colored("        🎆  FIREWORKS DISPLAY  🎆", 'bright_yellow', bold=True)
            print("\n" * 2)
            
            for _ in range(10):
                firework = random.choice(fireworks)
                color = random.choice(['red', 'yellow', 'orange', 'magenta', 'cyan'])
                spaces = " " * random.randint(10, 50)
                self.print_colored(f"{spaces}{firework}", color, bold=True)
            
            time.sleep(0.5)
    
    def print_wishes(self):
        """Print Diwali wishes"""
        wishes = [
            "May the divine light of Diwali spread into your life",
            "Peace, prosperity, and happiness! ✨",
            "",
            "May the festival of lights brighten up your life",
            "With happiness, joy, and prosperity! 🪔",
            "",
            "Wishing you and your family a very Happy Diwali! 🎆",
            "",
            "May this Diwali bring you:",
            "  ✦ Good Health",
            "  ✦ Wealth & Prosperity",
            "  ✦ Happiness & Joy",
            "  ✦ Success in all endeavors",
        ]
        
        print("\n")
        for wish in wishes:
            self.print_colored(wish, 'gold', bold=True)
            time.sleep(0.3)
    
    def display_menu(self):
        """Display the main menu"""
        print("\n")
        self.print_colored("═" * 60, 'gold')
        self.print_colored("  DIWALI CELEBRATION MENU", 'bright_yellow', bold=True)
        self.print_colored("═" * 60, 'gold')
        print("\n")
        print("  1. 🪔  Light a Diya")
        print("  2. 🎨  Display Rangoli")
        print("  3. 🎆  Watch Fireworks")
        print("  4. 💌  Read Diwali Wishes")
        print("  5. 🎉  Full Celebration (All of the above)")
        print("  6. 🚪  Exit")
        print("\n")
        self.print_colored("═" * 60, 'gold')
    
    def light_diya(self):
        """Light a diya animation"""
        self.clear_screen()
        print("\n" * 2)
        self.print_colored("        Lighting the Diya... 🪔", 'orange', bold=True)
        print("\n" * 2)
        self.print_diya('orange')
        print("\n")
        self.print_colored("        May this light bring joy to your home! ✨", 'gold', bold=True)
        time.sleep(2)
    
    def display_rangoli(self):
        """Display rangoli pattern"""
        self.clear_screen()
        print("\n" * 2)
        self.print_colored("        Beautiful Rangoli Design 🎨", 'magenta', bold=True)
        print("\n" * 2)
        self.print_rangoli()
        print("\n")
        self.print_colored("        Colors of joy and celebration! 🌈", 'cyan', bold=True)
        time.sleep(2)
    
    def full_celebration(self):
        """Run the full celebration sequence"""
        self.clear_screen()
        self.print_banner()
        time.sleep(2)
        
        self.light_diya()
        time.sleep(1)
        
        self.display_rangoli()
        time.sleep(1)
        
        self.print_fireworks()
        time.sleep(1)
        
        self.clear_screen()
        self.print_banner()
        self.print_wishes()
        time.sleep(3)
    
    def run(self):
        """Main application loop"""
        self.clear_screen()
        self.print_banner()
        time.sleep(2)
        
        while self.running:
            self.clear_screen()
            self.print_banner()
            self.display_menu()
            
            try:
                choice = input("\n  Enter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.light_diya()
                elif choice == '2':
                    self.display_rangoli()
                elif choice == '3':
                    self.print_fireworks()
                elif choice == '4':
                    self.clear_screen()
                    self.print_banner()
                    self.print_wishes()
                    time.sleep(3)
                elif choice == '5':
                    self.full_celebration()
                elif choice == '6':
                    self.clear_screen()
                    print("\n")
                    self.print_colored("  Thank you for celebrating Diwali with us! 🪔✨", 'gold', bold=True)
                    self.print_colored("  Shubh Deepavali! 🎆", 'bright_yellow', bold=True)
                    print("\n")
                    self.running = False
                else:
                    self.print_colored("\n  Invalid choice! Please try again.", 'red')
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.clear_screen()
                print("\n")
                self.print_colored("  Goodbye! Happy Diwali! 🪔", 'gold', bold=True)
                print("\n")
                self.running = False
                break
            except Exception as e:
                self.print_colored(f"\n  Error: {e}", 'red')
                time.sleep(2)


def main():
    """Main entry point"""
    print("\n")
    print("=" * 60)
    print("  DIWALI CELEBRATION APP")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    time.sleep(1)
    
    app = DiwaliApp()
    app.run()


if __name__ == "__main__":
    main()
