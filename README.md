# 🎮 Pong 2D

A sleek, high-performance **Minimalist 2D Arcade Pong game** built in **Python** using **Pygame** — complete with **Online TCP Socket Multiplayer**, **Both-Side Ready System**, **In-Game Chat**, **Dynamic Particle Effects**, **Procedural Synth Audio**, **Match Statistics Dashboard**, **Automated Test Suite**, and a **Standalone Executable (.EXE) Builder**!

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?logo=pygame&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen)
![Multiplayer](https://img.shields.io/badge/Online-Multiplayer-cyan)
![EXE](https://img.shields.io/badge/Standalone-.EXE-orange)
![FPS](https://img.shields.io/badge/FPS-60-brightgreen)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Features

- 🕹️ **4 Game Modes**:
  - **Single-Player (vs AI)**: 4 distinct difficulty tiers (*Easy*, *Medium*, *Hard*, *Impossible*) powered by real-time predictive trajectory calculations.
  - **2-Player Local**: Play head-to-head on the same keyboard.
  - **Online Host**: Host an online game room on your local IP/network.
  - **Online Join**: Join a friend's hosted game room anywhere on your LAN or over the internet.
- 💬 **In-Game Chat System**: Press **`T`** or **`Enter`** during online matches to send real-time messages to your opponent.
- ✅ **Both-Side Ready Confirmation**: Matches only start when both Host and Joiner confirm they are **`READY`** (press **`SPACE`**).
- 🛡️ **Windows Firewall Pre-Prompt**: Automated socket initialization triggers native OS Windows Defender Firewall network access prompts on launch.
- ⚡ **5 Dynamic Power-Ups**:
  - **Speed Ball (`S`)**: Boosts ball velocity for sudden fast-paced attacks.
  - **Goal Shield (`W`)**: Constructs a protective energy barrier behind your paddle.
  - **Paddle Extend (`E`)**: Enlarges paddle height by 50% for improved defense.
  - **Multi-Ball (`M`)**: Spawns an additional active ball into play.
  - **Slow-Mo (`T`)**: Temporal warp that reduces ball speed by 40% for strategic precision.
- ✨ **Dynamic Visual & Particle FX**: Tapered motion trails, high-speed particle sparks, expanding shockwave rings on goal explosion, and camera screen shake.
- 🎵 **Procedural Audio Synthesizer**: Self-contained sound engine generating retro audio waveforms directly in memory — zero external media asset dependencies required!
- 📊 **Post-Match Statistics Dashboard**: Comprehensive game-over summary card displaying final score breakdown, longest rally record, and peak ball velocity.
- 🧪 **Automated Test Suite**: Full `pytest` / `unittest` coverage validating ball reflection physics, paddle boundaries, powerups, AI logic, and state management.
- 📦 **Standalone Windows Executable (.EXE)**: Package the complete game into a single `Pong2D.exe` file using PyInstaller!

---

## ⚡ Dynamic Power-Ups

| Code | Power-Up Name | Color | Effect |
| :---: | :--- | :--- | :--- |
| **`S`** | **SPEED** | Red (`#EF4444`) | Multiplies ball speed by 1.5x for aggressive offense |
| **`W`** | **SHIELD** | Emerald (`#10B981`) | Spawns a rear wall barrier that absorbs 1 goal |
| **`E`** | **EXTEND** | Amber (`#F59E0B`) | Increases paddle height by 50% for 5 seconds |
| **`M`** | **MULTIBALL** | Indigo (`#6366F1`) | Clones ball into active dual-ball play |
| **`T`** | **SLOW-MO** | Cyan (`#06B6D4`) | Reduces ball velocity by 40% for temporal control |

---

## 🌐 How to Play Online with a Friend

### 1. Host Player (Starting the Game Room)
1. Launch `Pong2D.exe` (or run `python main.py`).
2. Click `MODE` until it displays **`MODE: ONLINE HOST`**.
3. Click **`START MATCH`**.
4. Note down your **LAN IP address** shown on screen (e.g. `192.168.1.15`) and share it with your friend.
5. If prompted by Windows Defender Firewall, check both **Private** and **Public** networks and click **Allow Access**.

### 2. Joiner Player (Connecting to Friend)
1. Launch `Pong2D.exe` on their computer.
2. Click `MODE` until it displays **`MODE: ONLINE JOIN`**.
3. Click **`START MATCH`**, type the host's IP address, and click **`CONNECT`**.

### 3. Pre-Match Ready System & Chat
- Once connected, press **`SPACEBAR`** (or click **`TOGGLE READY`**).
- When both players are Ready, the match countdown starts!
- Press **`T`** or **`ENTER`** anytime to type and send live chat messages.

---

## 🎮 Game Controls

| Action / Player | Key / Control |
| :--- | :--- |
| **Toggle Ready Status** | **`SPACEBAR`** or Click `TOGGLE READY` Button |
| **Open Chat Box** | **`T`** or **`ENTER`** |
| **Send Chat Message** | **`ENTER`** |
| **Cancel Chat Input** | **`ESC`** |
| **Player 1 (Left Paddle)** | `W` (Move Up) / `S` (Move Down) |
| **Player 2 (Right Paddle)** | `Up Arrow` (Move Up) / `Down Arrow` (Move Down) |
| **Pause / Resume** | `ESC` or `P` |
| **Mute / Unmute Sound** | `M` |
| **Quick Restart Match** | `R` |

---

## 🧪 Running Automated Tests

Run the complete test suite locally to verify physics, AI, and game states:

```bash
python -m pytest
```

---

## 📦 How to Build the `.exe` File

To compile `Pong2D.exe` to share with friends:

```bash
python build_exe.py
```
The compiled standalone executable will be saved in the `dist/` directory:
```
dist/Pong2D.exe
```

---

## 🚀 Quick Start (Running Source Code)

```bash
# Install Dependencies
pip install pygame pytest

# Launch Game GUI
python main.py

# (Optional) Launch Dedicated Headless Server
python server.py
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
