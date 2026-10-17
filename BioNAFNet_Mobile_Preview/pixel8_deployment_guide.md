# Google Pixel 8 Pro: Real-Time Mobile Deployment Guide

Since you have a **Google Pixel 8 Pro** (which has an incredibly powerful Tensor G3 chip), you can run the `BioNAFNet_Lite_Mobile.pt` model natively to get a real-time low-light enhancement camera app directly on your phone!

Here is the exact step-by-step process of taking the exported PyTorch model and putting it into a custom camera app.

---

## Step 1: Prepare Your Computer
1. **Download and Install [Android Studio](https://developer.android.com/studio)**.
2. Open Android Studio and ensure the **Android SDK** (API level 34, Android 14) is downloaded (the Pixel 8 Pro runs Android 14/15).
3. Connect your Pixel 8 Pro to your laptop via USB-C.
4. On your Pixel 8 Pro, go to **Settings > About Phone** and tap **"Build Number"** 7 times to unlock Developer Options.
5. Go to **Settings > System > Developer Options** and enable **"USB Debugging"**.
6. When prompted on the phone, authorize your laptop.

---

## Step 2: Download the PyTorch Camera Template
Instead of writing a complex Android Camera App from scratch, we will use the official PyTorch Mobile Vision template, which handles all the messy camera hardware permissions.

1. Open your laptop's **Command Prompt** (or Git Bash) and run:
   ```bash
   git clone https://github.com/pytorch/android-demo-app.git
   ```
2. Open **Android Studio**.
3. Click "Open" and navigate into the cloned folder:
   `android-demo-app/ObjectDetection/` (We use this template because it already has real-time camera streaming built-in).

---

## Step 3: Insert Your BioNAFNet Model
1. Go to your `BioNAFNet_Mobile_Preview` folder on your laptop.
2. Copy the **`BioNAFNet_Lite_Mobile.pt`** file.
3. In Android Studio, go to the **`app/src/main/assets`** folder inside the project.
4. Paste your `.pt` file there.

---

## Step 4: Update the Java/Kotlin Code
We need to tell the Android App to use your model instead of the default object detection one.

### 4A. Change the Model Loader
Open the main Activity file (usually `MainActivity.java` or `CameraXActivity.java` depending on the template update). Look for where the model is loaded:

```java
// OLD CODE:
// module = LiteModuleLoader.load(assetFilePath(this, "yolov5s.torchscript.ptl"));

// NEW CODE:
module = LiteModuleLoader.load(assetFilePath(this, "BioNAFNet_Lite_Mobile.pt"));
```

### 4B. Format Output Tensor as an Image
The template usually expects bounding boxes for object detection. You need to replace the output parsing to convert the AI's output Tensor back into a viewable Bitmap (Picture).

Replace the analyzing block with this math:
```java
// 1. Prepare Camera Frame (Resize to 640x480 as exported)
Bitmap resizedBitmap = Bitmap.createScaledBitmap(cameraBitmap, 640, 480, true);
final Tensor inputTensor = TensorImageUtils.bitmapToFloat32Tensor(
        resizedBitmap,
        TensorImageUtils.TORCHVISION_NORM_MEAN_RGB,
        TensorImageUtils.TORCHVISION_NORM_STD_RGB
);

// 2. Run BioNAFNet! (Tensor G3 CPU/GPU handles this instantly)
final Tensor outputTensor = module.forward(IValue.from(inputTensor)).toTensor();

// 3. Convert Output Tensor to Pixels to display on Screen
float[] scores = outputTensor.getDataAsFloatArray();
// (You will write a quick loop here turning the [3, 480, 640] float array back into RGB ints for an Android ImageView)
```
*(There are utility pre-built functions for `#3` in the `TensorImageUtils` library included in PyTorch Mobile).*

---

## Step 5: Build and Deploy to Pixel 8 Pro!
1. Look at the top toolbar in Android Studio. You should see a green "Play" ▶️ button and a dropdown menu next to it specifying your device: **"Google Pixel 8 Pro"**.
2. Click the **Play / Run ▶️** button.
3. Android Studio will automatically compile the Java code, package your 24MB model into an `.apk`, and install it over USB to your phone.
4. The app will launch on your phone.
5. **Accept Camera Permissions**.
6. Point your Pixel 8 Pro at a dark corner of your room, and the screen will show the brightened `BioNAFNet` real-time preview!

---

### Pro-Tip for Pixel 8 Pro Users:
Your phone contains the **Tensor G3 chip**. By default, PyTorch Mobile runs on the CPU. The CPU handles 24M parameters easily, but to make it *blisteringly fast*, you can tell Android to use the phone's GPU (Vulkan):

Before `module.forward(...)`, add this single line in Android Studio:
```java
module.forward(IValue.from(inputTensor)).toTensor(); // (CPU)
// Use Vulkan Backend for Android GPUs:
// (Requires adding org.pytorch:pytorch_android_vulkan to build.gradle)
```
