import os
import sys
import subprocess

def build_executable():
    print("=" * 60)
    print(" PONG 2D - STANDALONE EXECUTABLE (.EXE) BUILDER")
    print("=" * 60)
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller is available.")
    except ImportError:
        print("[+] Installing PyInstaller dependency...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(project_dir, "main.py")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "Pong2D",
        "--distpath", os.path.join(project_dir, "dist"),
        "--workpath", os.path.join(project_dir, "build"),
        "--specpath", project_dir,
        main_py
    ]
    
    print("\n[+] Compiling Python game into standalone Windows .exe file...")
    print(f" Executing command: {' '.join(cmd)}\n")
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        exe_path = os.path.join(project_dir, "dist", "Pong2D.exe")
        print("\n" + "=" * 60)
        print(" BUILD SUCCESSFUL!")
        print(f" Executable created at: {exe_path}")
        print("=" * 60)
        print(" You can now launch 'Pong2D.exe' to play!")
    else:
        print("\n[ERROR] Build failed with exit code:", res.returncode)

if __name__ == "__main__":
    build_executable()
