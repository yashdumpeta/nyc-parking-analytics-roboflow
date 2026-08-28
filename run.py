"""
Single-command launcher for the NYC Parking Analytics Fullstack Platform.
Starts the FastAPI backend and React (Vite) frontend concurrently,
synchronizes health checks, opens the browser, and ensures clean process teardown.

Usage:
    python run.py
"""

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


def wait_for_service(url: str, timeout: float = 15.0) -> bool:
    """Waits for an HTTP endpoint to return HTTP 200."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionResetError, OSError):
            time.sleep(0.3)
    return False


def main():
    print("=" * 68)
    print("🏙️   NYC Curb Telemetry & Revenue Engine (Fullstack Platform)")
    print("=" * 68)

    python_bin = sys.executable

    # 1. Launch FastAPI Backend
    print("\n[1/2] 🔌 Launching FastAPI AI Inference Backend on http://127.0.0.1:8000 ...")
    api_cmd = [
        python_bin,
        "-m",
        "uvicorn",
        "api:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    api_proc = subprocess.Popen(api_cmd, cwd=PROJECT_ROOT)

    # Wait for API health check
    print("      Waiting for FastAPI backend health check...")
    if wait_for_service("http://127.0.0.1:8000/"):
        print("      ✅ Backend is healthy and ready.")
    else:
        print("      ⚠️ Backend health check timed out. Proceeding...")

    # 2. Launch Vite React Frontend
    print("\n[2/2] ⚛️  Launching Modern React Dashboard on http://localhost:5173 ...")
    frontend_cmd = ["npm", "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

    print("\n" + "=" * 68)
    print("🚀  All services are running!")
    print("    • Modern React Dashboard: http://localhost:5173")
    print("    • Backend API & Stream:   http://127.0.0.1:8000")
    print("    • Interactive API Docs:   http://127.0.0.1:8000/docs")
    print("=" * 68)
    print("Press Ctrl+C to shut down both services cleanly.\n")

    # Open browser automatically
    time.sleep(1.0)
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    def cleanup(signum=None, frame=None):
        print("\n[System] Gracefully terminating all processes...")
        for proc, name in [(frontend_proc, "React Frontend"), (api_proc, "FastAPI Backend")]:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("[System] All services stopped cleanly.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        cleanup()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
