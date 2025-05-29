import time
import cv2
import degirum as dg
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
import asyncio

# Load Hailo model
inference_host_address = "@local"
zoo_url = "degirum/hailo"
token = ""
device_type = "HAILORT/HAILO8L"
model_name = "yolov8n_relu6_coco--640x640_quant_hailort_hailo8l_1"

model = dg.load_model(
    model_name=model_name,
    inference_host_address=inference_host_address,
    zoo_url=zoo_url,
    token=token,
    device_type=device_type
)

# FastAPI setup
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "templates" / "static")),
    name="static",
)


# Routes for index page
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Modifiey code from https://github.com/PiWebswiss/raspberry_PI5_hailo/blob/web-app/WebSocket/main.py
# WebSocket endpoint for real-time video streaming with FPS
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Initialize camera
    cap = cv2.VideoCapture(0)

    # Check that the camera is accessible
    # code from : https://chatgpt.com/share/683867a8-db8c-800e-ae13-1b2fcdfee4ee
    if not cap.isOpened():
        print("⚠️  No camera detected!")
        # Reject WebSocket with proper close code
        await websocket.close(code=1003)  # 1003 = unsupported data 
        return

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    prev_frame_time = time.time()

    # Accept the WebSocket connection
    await websocket.accept()

    try:
        while True:
            # Read a frame from the camera in a background thread
            ret, frame = await asyncio.to_thread(cap.read)
            if not ret:
                break  # Stop if the camera failed

            # Run inference on the frame (also off the main async thread)
            inf = await asyncio.to_thread(model, frame)
            frm = inf.image_overlay

            # Calculate and draw FPS on the frame
            now = time.time()
            fps = 1 / (now - prev_frame_time)
            prev_frame_time = now
            cv2.putText(frm, f"FPS: {fps:.0f}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0), 2, cv2.LINE_AA)

            # Encode the annotated frame as JPEG
            success, jpg = cv2.imencode('.jpg', frm)
            if not success:
                continue  # Skip this frame if encoding fails

            # Try to send the JPEG over WebSocket
            try:
                await websocket.send_bytes(jpg.tobytes())
            except Exception:
                # If the client disconnected or network error → exit loop
                print("Send stopped (client disconnected?)")
                break

    finally:
        # Always release the camera
        cap.release()

        # Gracefully close the WebSocket if it's still open
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.close()

  

            



