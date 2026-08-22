# 🎮 Neon Pong 2D

A feature-rich, high-performance **2D Cyberpunk Retro Arcade Pong game** built in **Python** using **Pygame** — built completely without HTML or CSS.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?logo=pygame&logoColor=white)
![FPS](https://img.shields.io/badge/FPS-60-brightgreen)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Features

- 🕹️ **2 Game Modes**:
  - **Single-Player (vs AI)**: 4 distinct difficulty tiers (*Easy*, *Medium*, *Hard*, *Impossible*) powered by real-time predictive trajectory calculations.
  - **2-Player Local**: Play head-to-head on the same keyboard.
- 🎨 **Neon Cyberpunk Aesthetics**: Deep space slate background, glowing cyan and magenta paddles, dynamic motion blur ball trails, particle impact sparks, and screen shake haptics.
- 🎵 **Procedural Audio Synthesizer**: Self-contained sound engine generating retro audio waveforms directly in memory (paddle bounce, wall hit, goal score sweep, power-up chime, victory fanfare) — zero external media asset dependencies required!
- ⚡ **Dynamic Power-Ups**:
  - ⚡ **Speed Ball**: Accelerates ball velocity.
  - 🛡️ **Goal Shield**: Spawns a protective barrier behind the goal line.
  - 📏 **Paddle Extend**: Increases paddle height by 50%.
  - 🎱 **Multi-Ball**: Spawns an extra ball into play.
- ⚙️ **HUD & Custom Settings**: Configurable target score (3, 5, 10, 15 points), power-up toggle, live rally counter, real-time ball speed meter, and mute sound toggle.
- ❌ **Quit Game Buttons**: Integrated Quit buttons in Main Menu, Pause Overlay, and Game Over screens.

---

## 🎮 Game Controls

| Action / Player | Key / Control |
| :--- | :--- |
| **Player 1 (Left Paddle)** | `W` (Move Up) / `S` (Move Down) |
| **Player 2 (Right Paddle)** | `Up Arrow` (Move Up) / `Down Arrow` (Move Down) |
| **Pause / Resume** | `ESC` or `P` |
| **Mute / Unmute Sound** | `M` |
| **Quick Restart Match** | `R` |

---

## 🚀 Quick Start & Installation

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/Av1jit/pong.git
cd pong
```

### 2. Install Dependencies
```bash
pip install pygame
```

### 3. Run the Game
```bash
python main.py
```

---

## 📁 Repository Structure

```
pong/
├── main.py            # Entrypoint, window setup & 60 FPS loop
├── game.py            # Main game state coordinator & event loop
├── paddle.py          # Paddle entity & 4-tier AI algorithm
├── ball.py            # Ball physics, spin & glowing trail system
├── powerup.py         # Dynamic power-up spawner & active timers
├── particles.py       # 2D particle simulation for sparks & explosions
├── audio.py           # In-memory procedural PCM sound synthesizer
├── ui.py              # Neon theme layout renderer & buttons
├── README.md          # Project documentation
└── .gitignore         # Git ignore rules
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
