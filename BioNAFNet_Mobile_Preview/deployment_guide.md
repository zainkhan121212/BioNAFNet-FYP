# BioNAFNet Realtime Preview — Deployment Guide

This document explains exactly how to run your distilled `BioNAFNet-Lite` model on your laptop to get real-time webcam enhancement.

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Prerequisites & Setup](#2-prerequisites--setup)
3. [Running the Webcam Preview](#3-running-the-webcam-preview)
4. [Controls & Interface](#4-controls--interface)
5. [Troubleshooting Camera Issues](#5-troubleshooting-camera-issues)
6. [Exporting to Actual Mobile Phone](#6-exporting-to-actual-mobile-phone)

---

## 1. Project Overview
**Location:** `F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Mobile_Preview`

This folder is **completely standalone**. It contains everything you need to run low-light enhancement without the massive 154M parameter training code. 
- **`best_student.pth`**: The compressed 24M parameter model.
- **`realtime_preview.py`**: The script that hooks into your laptop webcam.
- **`export_mobile.py`**: The script that converts your `.pth` to a `.pt` file for Android/iOS.
- **`BioNAFNet_Lite_Mobile.pt`**: The already-exported, mobile-ready mathematical graph of your model.

---

## 2. Prerequisites & Setup
Make sure you have your standard PyTorch environment activated. 
Open your Anaconda Prompt (Miniconda/Conda) and type:

```bash
# 1. Activate the environment you used for training
conda activate Retinexformer_Env

# 2. Check if OpenCV is installed (required for webcam capturing)
python -c "import cv2; print('OpenCV is installed!')"
```
*(If OpenCV is missing, simply run `pip install opencv-python`)*

---

## 3. Running the Webcam Preview
To launch the side-by-side comparison window on your laptop:

1. Open **Anaconda Prompt**.
2. Navigate to the exact folder using the `cd` command:
   ```bash
   cd "F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Mobile_Preview"
   ```
   *(Note the quotes are required because of the space in "eye adaption")*
3. Run the script:
   ```bash
   python realtime_preview.py
   ```

**What to expect:**
- A window titled `BioNAFNet Real-Time Preview` will pop up.
- The **Left Side** is your dark, raw webcam feed.
- The **Right Side** is the AI-enhanced, brightened output.
- You should see an FPS counter hovering around **8 to 11 FPS** (on a GTX 1650).

---

## 4. Controls & Interface
While the webcam window is active, you can use the following keyboard shortcuts:

*   **Press `s`**: Saves a high-quality "Snapshot" of the current frame directly into the `BioNAFNet_Mobile_Preview` folder as `capture_TIMESTAMP.png`. Use this when you want to save a comparison of a really dark room.
*   **Press `q`**: Safely closes the webcam feed and shuts down the AI processing.

---

## 5. Troubleshooting Camera Issues

| Issue | Solution |
| :--- | :--- |
| **"Could not open webcam"** | If the script immediately closes with this error, OpenCV is looking at the wrong camera channel. <br><br>Open `realtime_preview.py` in an editor. Go to line **161**: `cap = cv2.VideoCapture(0)`. Change the `0` to a `1` or `-1` to cycle through your connected cameras. |
| **"Out of Memory (OOM) Error"** | The default resolution in the script is 640x480. If your GPU crashes, lower the `CAPTURE_WIDTH` (line 164) to `480` and `CAPTURE_HEIGHT` to `360`. |
| **Webcam is too bright to test** | If your room isn't dark enough to see the AI working properly, go to line **182** in the script and uncomment `frame = cv2.convertScaleAbs(frame, alpha=0.15, beta=0)`. This computationally darkens the webcam feed so the AI has to "rescue" it. |

---

## 6. Exporting to Actual Mobile Phone (Android/iOS)
If you want to move this off your laptop and onto an actual smartphone application, the Python script has already done the heavy lifting.

Look inside the folder for **`BioNAFNet_Lite_Mobile.pt`**.
This format is specifically optimized for **PyTorch Mobile Lite Interpreter**.

**To build an Android App:**
1. You hand this `.pt` file to an Android developer (or load it into Android Studio).
2. They will follow the [PyTorch Mobile Android Quickstart Guide](https://pytorch.org/mobile/android/).
3. They use Java/Kotlin to capture the phone's camera, pass the frame into the `.pt` file, and display the output tensor on the phone screen. No Python is required!
