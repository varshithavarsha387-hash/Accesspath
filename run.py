"""
AccessPath – Real-Time Accessibility Navigation
Integrated Full-Stack Application Launcher
"""

import os
import sys
import socket
import subprocess
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def is_port_bindable(port, host="127.0.0.1"):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.close()
        return True
    except OSError:
        return False

def find_available_port(candidate_ports):
    for p in candidate_ports:
        if is_port_bindable(p):
            return p
    return None

def start_backend(port):
    print(f"\n[AccessPath] Starting FastAPI Backend on http://127.0.0.1:{port} ...")
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--reload"
    ]
    return subprocess.Popen(cmd, cwd=BACKEND_DIR, env=env)

def start_frontend(backend_port):
    print(f"[AccessPath] Starting React / Vite Frontend ...")
    env = os.environ.copy()
    env["VITE_API_URL"] = f"http://127.0.0.1:{backend_port}"
    cmd = "npm run dev"
    return subprocess.Popen(cmd, cwd=FRONTEND_DIR, env=env, shell=True)

def main():
    print("=" * 65)
    print("   AccessPath – Real-Time Accessibility Navigation")
    print("   AI-Powered Route Guidance & Barrier Auditing Platform")
    print("=" * 65)

    backend_port = 8000
    if not is_port_bindable(backend_port):
        # Find next open port if 8000 is occupied
        backend_port = find_available_port([8001, 8080, 8088, 8888]) or 8000

    backend_proc = start_backend(backend_port)
    time.sleep(2)
    frontend_proc = start_frontend(backend_port)

    print("\n" + "=" * 65)
    print("  [AccessPath Ready to Use]")
    print(f"  -> Frontend App: http://localhost:5173 (or assigned port)")
    print(f"  -> Backend API:  http://127.0.0.1:{backend_port}")
    print(f"  -> API Docs:     http://127.0.0.1:{backend_port}/docs")
    print("=" * 65)
    print("\nPress Ctrl+C in this terminal window anytime to stop.\n")

    def shutdown(sig, frame):
        print("\n[AccessPath] Shutting down services cleanly...")
        try:
            backend_proc.terminate()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print(f"[AccessPath] Backend process exited (code {backend_proc.returncode}).")
                break
            if frontend_proc.poll() is not None:
                print(f"[AccessPath] Frontend process exited (code {frontend_proc.returncode}).")
                break
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
