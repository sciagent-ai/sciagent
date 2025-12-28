# 🎊 New Year's Message App 🎊

A festive application to celebrate the New Year 2026 with interactive messages, animations, and fireworks!

## 📁 Files

- **new_years_message.py** - Interactive Python terminal application
- **new_years_message.html** - Beautiful web-based version with animations
- **README_NEW_YEARS.md** - This documentation file

## 🚀 Quick Start

### Python Version (Terminal)

Run the interactive terminal application:

```bash
python3 runs/new_years_message.py
```

Or make it executable and run directly:

```bash
chmod +x runs/new_years_message.py
./runs/new_years_message.py
```

### HTML Version (Web Browser)

Simply open the HTML file in your web browser:

```bash
open runs/new_years_message.html
```

Or on Linux:

```bash
xdg-open runs/new_years_message.html
```

Or on Windows:

```bash
start runs/new_years_message.html
```

## ✨ Features

### Python Terminal App

The Python version offers an interactive menu with the following options:

1. **Display New Year Banner** - Shows a decorative ASCII art banner
2. **Show Countdown** - Animated countdown from 5 to 1
3. **Fireworks Animation** - ASCII art fireworks display
4. **New Year Message** - Personalized wishes for the new year
5. **Show All** - Displays all features in sequence
6. **Exit** - Close the application

#### Features:
- 🎨 Colorful ASCII art and decorations
- ⏰ Interactive countdown animation
- 🎆 ASCII fireworks display
- 💬 Personalized New Year messages
- 🎯 Easy-to-use menu system
- ⌨️ Keyboard interrupt handling

### HTML Web App

The HTML version provides a stunning visual experience:

#### Features:
- 🌟 Beautiful gradient background
- ✨ Animated text with glowing effects
- 🎆 Interactive fireworks launcher
- ⏰ Countdown timer with animations
- 🌠 Twinkling stars background
- 📱 Responsive design for all devices
- 🎨 Smooth animations and transitions
- 🎯 Interactive buttons

#### Interactive Elements:
- **Launch Fireworks Button** - Creates colorful firework explosions
- **Countdown Button** - Starts a 5-second countdown with celebration
- **Auto-fireworks** - Fireworks launch automatically every 5 seconds

## 🎨 Customization

### Python Version

You can customize the messages by editing the `get_new_year_message()` function:

```python
def get_new_year_message():
    messages = [
        # Add your custom messages here
    ]
    return "\n".join(messages)
```

### HTML Version

Customize colors, animations, and styles in the `<style>` section:

```css
/* Change background gradient */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Modify text colors */
.year {
    background: linear-gradient(45deg, #FFD700, #FFA500, #FF69B4, #00CED1);
}
```

## 🎯 Use Cases

- **New Year Celebrations** - Display during New Year's Eve parties
- **Digital Greetings** - Send to friends and family
- **Office Celebrations** - Show on screens during office parties
- **Learning Project** - Study Python animations and HTML/CSS effects
- **Presentation Opener** - Use as an engaging presentation starter

## 🛠️ Technical Details

### Python Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)
- Cross-platform compatible (Windows, macOS, Linux)

### HTML Requirements
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- No server required - runs entirely in the browser
- JavaScript enabled

## 📝 Code Structure

### Python App Structure
```
new_years_message.py
├── print_banner()          # ASCII art banner
├── print_countdown()       # Countdown animation
├── print_fireworks()       # Fireworks animation
├── get_new_year_message()  # Personalized messages
├── display_interactive_menu() # Main menu loop
└── main()                  # Entry point
```

### HTML App Structure
```
new_years_message.html
├── Styles
│   ├── Animations (glow, fade, slide)
│   ├── Gradients and colors
│   └── Responsive design
├── Content
│   ├── Title and year display
│   ├── Wishes list
│   └── Interactive buttons
└── JavaScript
    ├── createStars()       # Background stars
    ├── launchFireworks()   # Firework effects
    └── playCountdown()     # Countdown timer
```

## 🎉 Examples

### Python Terminal Output
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🎆  HAPPY NEW YEAR 2026!  🎆                    ║
║                                                           ║
║              ✨ Wishing You Joy ✨                       ║
║              🌟 Success & Prosperity 🌟                  ║
║              🎊 Throughout the Year 🎊                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### HTML Display
- Animated gradient text showing "2026"
- Glowing "Happy New Year" title
- Smooth fade-in animations for wishes
- Interactive fireworks on button click
- Twinkling stars in the background

## 🤝 Contributing

Feel free to enhance this app with:
- More animation effects
- Sound effects
- Additional interactive features
- Different themes
- Multilingual support

## 📄 License

This is a simple demonstration app. Feel free to use, modify, and share!

## 🎊 Happy New Year 2026! 🎊

May this year bring you joy, success, and wonderful memories!

---

Created with ❤️ for celebrating the New Year
