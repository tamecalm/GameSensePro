# GameSensePro - Sensitivity Toolkit

GameSensePro is a terminal-based toolkit designed to help mobile FPS gamers calculate, calibrate, and manage their in-game sensitivity settings for optimal performance. The toolkit provides a rich, interactive experience and supports multiple games, devices, and player styles.

---

**Author:** @tamecalm  
**Start Date:** 2025-05-25

---

## Features

- **Device Detection:** Automatically detects device model, brand, resolution, DPI, refresh rate, and gyro support.
- **Game Support:** Supports Blood Strike, Free Fire, Call of Duty Mobile, Delta Force, and PUBG Mobile.
- **Player Style Customization:** Adjusts sensitivity based on number of fingers used, skill level, aiming finger, and claw grip.
- **Community News Integration:** Incorporates recent community sentiment and news to refine recommendations.
- **Feedback Collection:** Lets users provide feedback to improve future sensitivity calculations.
- **Statistics Viewer:** Tracks and displays calculation and feedback history.
- **Stats Management:** Allows users to clear their stats/history.
- **Multi-language Support:** Choose from 10+ languages at startup.
- **Rich Terminal UI:** Uses [rich](https://github.com/Textualize/rich) for colorful, interactive output and animations.
- **Data Storage:** Saves calculation results and feedback for later review.
- **Menu-driven Navigation:** Simple, clear menus for all actions.
- **Exit Panel:** Stylish exit message with timestamp.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/tamecalm/GameSensePro.git
   cd GameSensePro
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

   > **Note:** On Android/Termux, you may need to install `termux-api` for gyro detection:
   > ```sh
   > pkg install termux-api
   > ```

## Usage

Run the main script:

```sh
python main.py
```

Follow the prompts to select your language, game, and provide device/player details. Use the menu to calculate sensitivity, give feedback, view or clear stats, or exit.

## Project Structure

```
main.py
requirements.txt
modules/
    device/
    language/
    sensitivity/
    stats/
    ui/
    utils/
data/
```

- **modules/**: Core logic and utilities.
- **data/**: Stores results, logs, and mappings.

## Requirements

- Python 3.7+
- See [requirements.txt](requirements.txt) for dependencies:
  - requests
  - beautifulsoup4
  - rich

## Contributing

Pull requests and suggestions are welcome! Please open an issue for major changes.

## License

MIT License

---