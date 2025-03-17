from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI()

# Store active websocket connections
connected_clients = set()

# Basic web page for sending Commands
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Assistant Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 {
            color: #333;
        }

        #command {
            width: 300px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-right: 10px;
            font-size: 16px;
        }

        button {
            padding: 10px 15px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #218838;
        }

        #status {
            margin-top: 20px;
            font-size: 18px;
            color: #007bff;
        }

        #response {
            margin-top: 20px;
            font-size: 16px;
            color: #333;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            background-color: #fff;
            width: 300px;
            display: none; /* Initially hidden */
        }
    </style>
</head>
<body>
    <h1>Assistant Control Panel</h1>
    <input type="text" id="command" placeholder="Enter command">
    <button onclick="sendCommand()">Send</button>
    <p id="status"></p>
    <div id="response"></div>

    <script>
        // Use the window location to dynamically set the WebSocket URL
        var ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onopen = function(){
            document.getElementById("status").innerText = "Connected!";
        };

        ws.onmessage = function(event) {
            console.log("Response from server:", event.data);
            document.getElementById("response").innerText = "Response: " + event.data;
            document.getElementById("response").style.display = "block"; // Show response
        };

        function sendCommand(){
            var command = document.getElementById("command").value;
            if (command.trim() !== "") {
                ws.send(command);
                document.getElementById("command").value = "";  // Clear input
            }
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    """Serve the web page."""
    return HTMLResponse(HTML_PAGE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time command transmission."""
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Receive text data
            print(f"Received command: {data}")

            # Broadcast command to all connected clients
            for client in connected_clients:
                await client.send_text(data)

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        connected_clients.remove(websocket)  # Remove disconnected clients

if __name__ == "__main__":
    # Use the port from the environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
