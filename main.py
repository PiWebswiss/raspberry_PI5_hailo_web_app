import time
import cv2
import degirum as dg
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

# 1. Load Hailo model
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

# 2. FastAPI setup
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
    await websocket.accept()

    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        prev_frame_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Run Hailo inference
            inference_frame = model(frame)
            annotated_frame = inference_frame.image_overlay

            # Calculate and overlay FPS
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time

            fps_text = f"FPS: {fps:.0f}"
            cv2.putText(annotated_frame, fps_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # Encode frame to JPEG (you can switch to WebP by replacing '.jpg' with '.webp')
            success, encoded_image = cv2.imencode('.jpg', annotated_frame)
            if not success:
                continue

            await websocket.send_bytes(encoded_image.tobytes())
    # Disconnect and close WebSocket if a problem occurs
    except WebSocketDisconnect:
        pass
    # Properly clean up your video capture
    finally:
        cap.release()
        await websocket.close()
  

            



