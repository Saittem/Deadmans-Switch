import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

from winotify import Notification, audio # Make sure winotify is installed: pip install winotify

# --- Configuration ---
SERVER_HOST = "localhost"
SERVER_PORT = 8888
CLICK_PATH = "/click" # The URL path the notification will hit

# --- Global Flag for Communication ---
# This flag will be set by the HTTP server thread and checked by the main thread.
CLICKED_FLAG = False

# --- HTTP Server Handler ---
class ClickHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler that sets the CLICKED_FLAG when the specific path is accessed.
    """
    def do_GET(self):
        global CLICKED_FLAG
        print(f"Server received GET request for: {self.path}")
        if self.path == CLICK_PATH:
            CLICKED_FLAG = True
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Notification Click Detected!</h1><p>You can close this tab.</p></body></html>")
            print("CLICKED_FLAG set to True.")
        else:
            self.send_response(204) # No Content
            self.end_headers()
            print(f"Unhandled path: {self.path}")

# --- HTTP Server Thread Function ---
def run_http_server():
    """
    Starts the HTTP server. This function should run in a separate thread.
    """
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, ClickHandler)
    print(f"HTTP server started on http://{SERVER_HOST}:{SERVER_PORT}")
    
    # Store the server instance so we can shut it down later
    global http_server_instance
    http_server_instance = httpd

    try:
        httpd.serve_forever() # Blocks until server is shut down
    except KeyboardInterrupt:
        print("\nHTTP server shutting down via KeyboardInterrupt...")
    finally:
        httpd.server_close() # Clean up resources
        print("HTTP server stopped.")

# --- Main Application Logic ---
def main_application_logic():
    """
    Contains the main application flow, including showing notification
    and checking the flag.
    """
    print("Main application logic started.")

    # 1. Start the HTTP server in a separate thread
    server_thread = threading.Thread(target=run_http_server, daemon=True) # daemon=True allows main program to exit even if thread is running
    server_thread.start()
    time.sleep(1) # Give the server a moment to start up

    # 2. Prepare and show the winotify notification
    notification_url = f"http://{SERVER_HOST}:{SERVER_PORT}{CLICK_PATH}"
    print(f"Notification launch URL: {notification_url}")

    toast = Notification(app_id="MyAppTest",
                         title="Action Required!",
                         msg="Please click the 'I'm Awake!' button.",
                         duration="long") # "long" keeps it on screen longer
    toast.set_audio(audio.Default, loop=False)
    toast.add_actions(label="I'm Awake!", launch=notification_url)
    
    try:
        toast.show()
        print("Notification shown. Waiting for click...")
    except Exception as e:
        print(f"Error showing notification: {e}")
        # If notification fails, we might still want to proceed or exit gracefully
        # For this example, let's just exit.
        return

    # 3. Poll the CLICKED_FLAG
    timeout_seconds = 60 # How long to wait for a click
    start_time = time.time()
    
    while not CLICKED_FLAG and (time.time() - start_time < timeout_seconds):
        sys.stdout.write(".") # Show progress
        sys.stdout.flush()
        time.sleep(1) # Check every second
    print("\n") # Newline after dots

    # 4. Act based on the flag
    if CLICKED_FLAG:
        print("Notification clicked! Launching Notepad...")
        notepad_path = r"C:\Windows\System32\notepad.exe"
        try:
            subprocess.Popen([notepad_path])
            print("Notepad launched successfully.")
        except FileNotFoundError:
            print(f"Error: Notepad not found at {notepad_path}. Please check path.")
        except Exception as e:
            print(f"Error launching Notepad: {e}")
    else:
        print(f"Timeout: Notification not clicked within {timeout_seconds} seconds.")

    print("Main application logic finished.")

# --- Entry Point ---
if __name__ == "__main__":
    http_server_instance = None # To hold the server object for graceful shutdown if needed

    try:
        main_application_logic()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user (Ctrl+C).")
    finally:
        # Attempt to shut down the HTTP server gracefully
        if http_server_instance:
            print("Attempting to shut down HTTP server...")
            # Use shutdown() in a separate thread as it might block waiting for current requests
            # For a simple local server, directly calling shutdown usually works fine,
            # but for robustness against ongoing requests, a separate thread for shutdown is better.
            threading.Thread(target=http_server_instance.shutdown).start()
            # http_server_instance.server_close() # This is handled by finally in run_http_server

        print("Exiting application.")