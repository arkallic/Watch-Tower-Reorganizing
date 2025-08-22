#!/usr/bin/env python3
"""
Watch Tower Dashboard Startup Script
Starts both the backend API and frontend development server
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class DashboardStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.dashboard_dir = Path(__file__).parent
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import fastapi
            import uvicorn
            import aiofiles
            print("✅ Python dependencies found")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("Install with: pip install fastapi uvicorn aiofiles python-multipart")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js found: {result.stdout.strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js 16+")
            return False
        
        # Check if npm install has been run
        node_modules = self.dashboard_dir / "frontend" / "node_modules"
        if not node_modules.exists():
            print("⚠️  Frontend dependencies not installed")
            print("Installing frontend dependencies...")
            
            try:
                subprocess.run(['npm', 'install'], 
                             cwd=self.dashboard_dir / "frontend", 
                             check=True)
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install frontend dependencies")
                return False
        else:
            print("✅ Frontend dependencies found")
        
        return True
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend server...")
        
        backend_dir = self.dashboard_dir / "backend"
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor backend output in a separate thread
            def monitor_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    print(f"[Backend] {line.strip()}")
            
            threading.Thread(target=monitor_backend, daemon=True).start()
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started on http://localhost:8000")
                return True
            else:
                print("❌ Backend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend development server"""
        print("🎨 Starting frontend development server...")
        
        frontend_dir = self.dashboard_dir / "frontend"
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['BROWSER'] = 'none'
            env['PORT'] = '3001'  # Force port 3001
            
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            
            # Monitor frontend output in a separate thread
            def monitor_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if 'webpack compiled' in line.lower() or 'compiled successfully' in line.lower():
                        print("✅ Frontend compiled successfully on http://localhost:3001!")
            
            threading.Thread(target=monitor_frontend, daemon=True).start()
            
            # Wait for compilation
            time.sleep(8)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend development server started on http://localhost:3001")
                return True
            else:
                print("❌ Frontend development server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
        
    def cleanup(self):
        """Clean up processes on exit"""
        print("\n🛑 Shutting down dashboard...")
        
        if self.backend_process:
            print("Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ Dashboard stopped")
    
    def run(self):
        """Main startup sequence"""
        print("🚀 Watch Tower Dashboard Startup")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            sys.exit(1)
        
        print("\n" + "=" * 50)
        
        # Start backend
        if not self.start_backend():
            sys.exit(1)
        
        # Start frontend
        if not self.start_frontend():
            self.cleanup()
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 Watch Tower Dashboard is ready!")
        print("📊 Dashboard: http://localhost:3000")
        print("🔧 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the dashboard")
        print("=" * 50)
        
        try:
            # Keep the main process alive
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the dashboard
    starter = DashboardStarter()
    starter.run()

if __name__ == "__main__":
    main()