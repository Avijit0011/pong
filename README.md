# 🎮 Pong 2D

A sleek, high-performance **Minimalist 2D Arcade Pong game** built in **Python** using **Pygame** — complete with **Online TCP Socket Multiplayer**, **Both-Side Ready System**, **In-Game Chat**, and a **Standalone Executable (.EXE) Builder**!

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?logo=pygame&logoColor=white)
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
- 📦 **Standalone Windows Executable (.EXE)**: Package the complete game into a single `Pong2D.exe` file that your friends can open and play without installing Python!
- 🌐 **Dedicated Server Script**: Optionally host headless game servers using `python server.py --port 5555`.
- 🎨 **Minimalist Aesthetics**: Deep slate background, sleek sky blue and rose red paddles, smooth motion trail, crisp micro-sparks, and subtle screen feedback.
- 🎵 **Procedural Audio Synthesizer**: Self-contained sound engine generating retro audio waveforms directly in memory — zero external media asset dependencies required!
- ⚡ **Dynamic Power-Ups**: Speed Ball, Goal Shield, Paddle Extend, Multi-Ball.
- ⚙️ **HUD & Custom Settings**: Configurable target score (3, 5, 10, 15 points), power-up toggle, live rally counter, and mute sound toggle.

---

## 🌐 How to Play Online with a Friend

### 1. Host Player (Starting the Game Room)
1. Launch `NeonPong2D.exe` (or run `python main.py`).
2. Click `MODE` until it displays **`MODE: ONLINE HOST 🌐`**.
3. Click **`START MATCH 🚀`**.
4. Note down your **LAN IP address** shown on screen (e.g. `192.168.1.15`) and share it with your friend.
5. If prompted by Windows Defender Firewall, check both **Private** and **Public** networks and click **Allow Access**.

### 2. Joiner Player (Connecting to Friend)
1. Launch `NeonPong2D.exe` on their computer.
2. Click `MODE` until it displays **`MODE: ONLINE JOIN 🔗`**.
3. Click **`START MATCH 🚀`**, type the host's IP address, and click **`CONNECT 🔗`**.

### 3. Pre-Match Ready System & Chat
- Once connected, press **`SPACEBAR`** (or click **`TOGGLE READY ✅`**).
- When both players are Ready, the match countdown starts!
- Press **`T`** or **`ENTER`** anytime to type and send live chat messages.

### 4. Playing Across the Internet (Over WAN)
To play with a friend outside your local Wi-Fi network:
1. The Host player runs a free lightweight tunnel like [ngrok](https://ngrok.com) or [Tailscale](https://tailscale.com):
   ```bash
   ngrok tcp 5555
   ```
2. Share the generated forwarding IP address with your friend to connect!

---

## 📦 How to Build the `.exe` File

To compile `NeonPong2D.exe` to share with friends:

```bash
python build_exe.py
```
The compiled standalone executable will be saved in the `dist/` directory:
```
dist/NeonPong2D.exe
```

---

## 🎮 Game Controls

| Action / Player | Key / Control |
| :--- | :--- |
| **Toggle Ready Status** | **`SPACEBAR`** or Click `TOGGLE READY ✅` Button |
| **Open Chat Box** | **`T`** or **`ENTER`** |
| **Send Chat Message** | **`ENTER`** |
| **Cancel Chat Input** | **`ESC`** |
| **Player 1 (Left Paddle)** | `W` (Move Up) / `S` (Move Down) |
| **Player 2 (Right Paddle)** | `Up Arrow` (Move Up) / `Down Arrow` (Move Down) |
| **Pause / Resume** | `ESC` or `P` |
| **Mute / Unmute Sound** | `M` |
| **Quick Restart Match** | `R` |

---

## 🚀 Quick Start (Running Source Code)

```bash
# Install Pygame
pip install pygame

# Launch Game GUI
python main.py

# (Optional) Launch Dedicated Headless Server
python server.py
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
