import time
import sys
import argparse
from network import NetworkServer, get_local_ip

def run_dedicated_server(port=5555):
    local_ip = get_local_ip()
    print("=" * 60)
    print(" NEON PONG 2D - DEDICATED GAME SERVER")
    print("=" * 60)
    print(f" Local LAN IP:   {local_ip}")
    print(f" Port:           {port}")
    print(f" Connect string: {local_ip}:{port}")
    print("=" * 60)
    
    server = NetworkServer(port=port)
    success, msg = server.start()
    if not success:
        print(f"[ERROR] {msg}")
        sys.exit(1)
        
    print(f"[OK] {msg}")
    print("[+] Waiting for Player 2 to join...")
    
    try:
        while True:
            if server.is_connected:
                print(f"[CONNECTED] Player connected from {server.client_addr[0]}:{server.client_addr[1]}")
                break
            time.sleep(0.5)
            
        print("[ACTIVE] Match session active. Press Ctrl+C to shut down server.")
        while server.is_connected:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down server...")
    finally:
        server.stop()
        print("[STOPPED] Server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neon Pong 2D Dedicated Server")
    parser.add_argument("--port", type=int, default=5555, help="Port to listen on (default 5555)")
    args = parser.parse_args()
    run_dedicated_server(args.port)
