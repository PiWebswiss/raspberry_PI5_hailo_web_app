## Raspberry Pi 5 Running Hailo Model with a FastAPI Server.


I'm using a Raspberry Pi 5 with a Hailo AI chip to detect objects in a video and stream the results live to a web page using FastAPI routes.

To use this application, please install the [DeGirum PySDK](https://github.com/DeGirum/hailo_examples/blob/main/README.md).

![alt text](templates/static/ressources/web_app_live.png)

---

### The repository contains the following components:

* The source code of the server
* Our pre-trained artificial intelligence model
* The web graphical interface (designed in HTML and CSS)
* You will also find the necessary scripts to:

  * Train the YOLO model
  * Compile the model for the Hailo accelerator

**Colab notebook to train the model:**
[Yolo train](https://colab.research.google.com/drive/1kkYMit4gj5RQPTyDT4U0StDJmXVad0Oz?usp=sharing)

**Colab notebook to compile the model for Hailo:**
[Compile hailo model](https://colab.research.google.com/drive/1cI-a5BHdVLQiYJJdzprg2WqeuU2pA_YQ?usp=drive_link)


---

### Install Requirements

```bash
pip install fastapi uvicorn
```

Make sure to also install the [DeGirum SDK](https://github.com/DeGirum/hailo_examples) as described in their documentation.

---

### To Run the Server

1. **Activate the ``degirum_env`` virtual environment**:

   ```bash
   source ../degirum_env/bin/activate
   ```

2. **Start the FastAPI server**:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. **Access Video Stream**:
   - Open a web browser and navigate to `http://127.0.0.1:8001/`view the AI-processed video stream.

