"""
FYP Final Report — Part 3: Chapters 6-7 (Implementation/Testing + Results)
HUMANIZED GHOST MODE TEXT
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FIGS = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
DOC  = r"F:\low_light_enhancement\eye adaption\BioNAFNet\LLIE_FYP_Final_Report.docx"
doc = Document(DOC)
FN=[1]; TN=[15]

def h1(t): doc.add_heading(t,1)
def h2(t): doc.add_heading(t,2)
def h3(t): doc.add_heading(t,3)
def para(t):
    p=doc.add_paragraph(t); p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent=Cm(1.27); return p
def pn(t):
    p=doc.add_paragraph(t); p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; return p
def bl(t): doc.add_paragraph(t, style='List Bullet')
def nl(t): doc.add_paragraph(t, style='List Number')
def fig(fn,cap,w=5.5):
    FN[0]+=1; path=os.path.join(FIGS,fn)
    if os.path.exists(path):
        doc.add_picture(path,width=Inches(w)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    c=doc.add_paragraph(f'Figure {FN[0]}: {cap}'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
    c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
def tbl(headers,rows,cap=None):
    TN[0]+=1
    if cap:
        c=doc.add_paragraph(f'Table {TN[0]}: {cap}'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
        c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    try: t.style='Table Grid'
    except: pass
    for j,h in enumerate(headers):
        cell=t.rows[0].cells[j]; cell.text=h
        for r in cell.paragraphs[0].runs: r.bold=True; r.font.size=Pt(10); r.font.name='Times New Roman'
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            cell=t.rows[i+1].cells[j]; cell.text=str(val)
            for r in cell.paragraphs[0].runs: r.font.size=Pt(10); r.font.name='Times New Roman'
    doc.add_paragraph('')
def photo(desc):
    p=doc.add_paragraph(); r=p.add_run(f'[INSERT PHOTO HERE]\nType: {desc}')
    r.bold=True; r.font.color.rgb=RGBColor(0xCC,0x00,0x00); r.font.size=Pt(11)
    r.font.name='Times New Roman'; p.alignment=WD_ALIGN_PARAGRAPH.CENTER

# ═══════════════════════════════════════════════════════════════
# CHAPTER 6: IMPLEMENTATION AND TESTING
# ═══════════════════════════════════════════════════════════════
h1('Chapter 6')
h2('Implementation and Testing')

h3('6.1 Implementation Overview')
para('We wrote this entire project in Python 3.10. For the AI stuff, we used PyTorch 2.0. To build the desktop app, we used CustomTkinter 5.2. By the end of it, we were looking at roughly 5,500 lines of code spread across 12 different files. We trained everything on an NVIDIA RTX graphics card using CUDA 12. We tried to keep the code neat, using docstrings and separating functions so it did not turn into spaghetti code.')

h3('6.2 Code Structure')
tbl(['File','Lines','Purpose'],
    [['train_bionafnet.py','~1100','The big script to train the Teacher model'],
     ['train_distillation.py','~1100','The script forcing the Student to copy the Teacher'],
     ['neon_enhancer_pro.py','2708','The GUI code for the actual desktop app'],
     ['model_hooks.py','430','The glue connecting the GUI to the 12 neural networks'],
     ['bionafnet_teacher.py','97','Pulls up the 154M Teacher'],
     ['bionafnet_student.py','96','Pulls up the 24M Student'],
     ['bionafnet_ensemble.py','46','Mashes the Teacher and Student together'],
     ['eval_lol_datasets.py','~800','Calculates test scores like PSNR and SSIM'],
     ['ensemble_test.py','~450','Testing the fusion setup'],
     ['benchmark_all_models.py','~450','Checks how fast each model runs'],
     ['infer_bionafnet.py','~700','Quick script to process one image']],
    'Project Code File Structure')

h3('6.3 Key Implementation Details')
pn('6.3.1 SimpleGate Mechanism')
para('Most AI models use a math function called ReLU. The issue with ReLU is that it just deletes any number below zero. You lose data. Instead, we used SimpleGate. It splits the data block in half and multiplies the top half by the bottom half. It sounds weird, but the original NAFNet paper proved it actually beats complex math functions.')

pn('6.3.2 Exponential Moving Average (EMA)')
para('During training, the AI\'s math weights bounce around wildly. So, we set up an Exponential Moving Average (EMA) script. Every time the AI takes a step, EMA makes a hidden backup copy of the weights. We set the decay to 0.9995. When we actually test the AI later, we use this "shadow" backup because it is much smoother and gives cleaner pictures than the raw weights.')

pn('6.3.3 Automatic Mixed Precision (AMP)')
para('To stop the GPU from running out of memory, we forced PyTorch to use 16-bit floating point math instead of 32-bit. But there was a catch. Our FAEB module uses Fourier Transforms for frequencies. When we ran Fourier Transforms in 16-bit, the math blew up and gave us errors. PyTorch\'s autocast feature helped us keep almost everything in 16-bit while forcing just the Fourier stuff back to 32-bit.')

pn('6.3.4 Padding Strategy')
para('The network shrinks the image 4 times during processing. If your image size does not perfectly divide by 16, the network crashes. We fixed this by adding reflection padding—basically mirroring the edges of the photo until the width and height are multiples of 16. After the AI finishes, we just chop those mirrored edges off.')

pn('6.3.5 Model Caching')
para('The Teacher model file is massive—about 2.5 GB. Loading that off the hard drive takes almost 10 seconds. We built a caching system in Python that loads it into memory once and keeps it there. So the first image takes 10 seconds to load, but the next 100 images process instantly.')

h3('6.4 NeonEnhancer Pro Application Features')
pn('6.4.1 Enhancement Page')
para('This is the main screen. You upload an image, or a whole folder of images. On the left, there is a dropdown to pick from 12 different AI models. There is also a switch to force processing onto your CPU or GPU. On the right, it shows a split screen giving you the original dark photo next to the clean AI version. You can click Next or Previous to click through a batch.')

photo('Screenshot of the Enhancement page after processing a batch of images. Description: Show the left panel with a model selected (e.g., BioNAFNet Student) and the right panel showing the before/after split with the gallery counter showing "1 / 15".')

pn('6.4.2 Augmentation Page')
para('We needed a way to fake more data for training. So we built this page. You upload an image and toggle a slider from 1 to 4. It will automatically spit out 4 random variations of that image. It flips them, rotates them, messes with the brightness, and adds noise, throwing them all into an output folder.')

photo('Screenshot of the Augmentation page showing the slider set to 3 variations and a preview of augmented images. Description: Show the control panel on the left with the augmentation count slider and the preview area on the right.')

pn('6.4.3 Cropping Page')
para('Sometimes you just want to cut the image. We added buttons to instantly crop the photo into a perfect square, a 16:9 widescreen layout, or a center punch. It shows a bounding box live on the screen so you can see what is getting cut.')

photo('Screenshot of the Cropping page showing an image with a crop region highlighted and the preset buttons (Square, Wide, Center) visible. Description: Show the crop controls on the left and the image preview with crop overlay on the right.')

pn('6.4.4 Resizing Page')
para('This page lets you shrink or blow up pictures. The most important thing here is the aspect ratio lock. If you lock it, you can change the width and the app will automatically math out the height so your picture does not look squished.')

photo('Screenshot of the Resizing page showing the width/height sliders and the aspect ratio lock toggle. Description: Show the resize controls with an image preview showing the current vs new dimensions.')

pn('6.4.5 Live Preview Page')
para('This is the coolest tab. It turns on your laptop webcam. The raw dark feed is on the left, and the AI-cleaned video feed is on the right. Because our Student model is so quick, it can actually process 20 frames per second of live video without lagging.')

photo('Screenshot of the Live Preview page showing webcam feed on the left and enhanced version on the right. Description: Show the real-time side-by-side comparison with the model name and FPS counter visible.')

h3('6.5 Training Process')
pn('6.5.1 Teacher Model Training')
para('Training the Teacher took forever. We ran it for 504 epochs on a massive pile of 2074 image pairs. We didn\'t feed it full images; we chopped them into 128x128 pixel squares so the GPU wouldn\'t crash. We set the learning rate to 2e-4 and told it to randomly restart using Cosine waves. Around epoch 476, it hit its best score of 25.05 dB.')

fig('fig_teacher_training.png', 'Teacher Model Training Curves (504 Epochs)')
fig('fig_teacher_val.png', 'Teacher Model Validation PSNR Over Training')

pn('6.5.2 Student Model Training (Distillation)')
para('Next, we trained the Student for 693 epochs. We locked the Teacher model so it could not learn anything new, and used it strictly to grade the Student. The Student tried to match the real bright photo (50% of its grade), tried to draw the shapes correctly (10%), and tried to copy whatever the Teacher did (40%). Strangely enough, the Student hit 25.09 dB, beating the Teacher slightly.')

fig('fig_student_training.png', 'Student Model Distillation Training Curves (693 Epochs)')
fig('fig_loss_comparison.png', 'Training Loss Comparison: Teacher vs Student')

h3('6.6 Testing Methodology')
pn('6.6.1 Quantitative Testing')
para('We ran math tests against our holdout images. We had 15 test photos for LOLv1, 100 for LOLv2 Real, and 100 for LOLv2 Synthetic. We checked PSNR for noise and SSIM for overall shape similarity.')

pn('6.6.2 Unit Testing')
tbl(['Test Case','Input','Expected','Result'],
    [['Model loads correctly','Teacher weights','No crash','Pass'],
     ['Student loads correctly','Student weights','No crash','Pass'],
     ['Padding math works','400x600 photo','Returns exactly 400x600','Pass'],
     ['Colors aren\'t broken','Any photo','RGB values stay between 0-255','Pass'],
     ['Actually fixes image','Dark photo','New PSNR is higher than old','Pass'],
     ['Batch saves properly','10 photos','10 finished files','Pass'],
     ['GPU math matches CPU','Same photo','Almost exact match','Pass'],
     ['Ram cache works','Run 2nd photo','Loads instantly','Pass'],
     ['Ensemble math works','Teacher + Student','Gets average math exact','Pass'],
     ['SSIM script','Known test image','Exactly matches known score','Pass']],
    'Unit Test Cases and Results')

pn('6.6.3 Integration Testing')
tbl(['Test Case','Components','Expected','Result'],
    [['App launches all 12 AIs','UI + loader','Dropdown actually works','Pass'],
     ['Graphics card button works','UI + PyTorch','Swaps properly without crashing','Pass'],
     ['Batch run doesn\'t freeze','UI + hard drive','Processes all photos','Pass'],
     ['Next/Back buttons','UI gallery','Swaps images seamlessly','Pass'],
     ['Math overlay pops up','UI math engine','Shows score screen if available','Pass'],
     ['Data Maker tool','UI PIL script','Spits out variations','Pass'],
     ['Crop tool cuts right','UI tools','1:1 actually makes a perfect square','Pass'],
     ['Slider locks','UI resize','No stretching images','Pass'],
     ['Webcam feeds video','UI camera hook','Draws frames to screen real time','Pass']],
    'Integration Test Cases and Results')

h3('6.7 Software Quality')
para('We tried to write this like a real piece of software, not just a messy student script. We split the UI code totally separate from the PyTorch math. We wrote notes explaining what every function does. We made sure to catch errors, like if a user forgot to download the 2GB network file before clicking run. We also put the AI processing on a separate computer thread so the app window would not freeze and say "Not Responding" while it was crunching math.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# CHAPTER 7: RESULTS AND DISCUSSION
# ═══════════════════════════════════════════════════════════════
h1('Chapter 7')
h2('Results and Discussion')

h3('7.1 Quantitative Results')
pn('7.1.1 PSNR and SSIM Benchmarks')
tbl(['Model Variant','LOLv1 PSNR','LOLv1 SSIM','LOLv2R PSNR','LOLv2R SSIM','LOLv2S PSNR','LOLv2S SSIM'],
    [['Teacher (154M, 2-pass)','24.94','0.8661','28.67','0.9101','26.22','0.9457'],
     ['Student-693 (24M, 1-pass)','25.23','0.8528','28.48','0.8942','25.75','0.9375'],
     ['Ensemble 50/50','25.27','0.8636','29.26','0.9081','26.47','0.9465'],
     ['Ensemble T60/S40','25.23','0.8641','29.29','0.9087','26.46','0.9462'],
     ['Ensemble T40/S60','25.29','0.8625','29.19','0.9069','26.43','0.9461'],
     ['Synergy T70/S30','24.96','--','28.90','--','26.33','--']],
    'Complete PSNR/SSIM Results for All Model Variants')

fig('fig_benchmark_psnr.png', 'PSNR Comparison Across All Models and Datasets')
fig('fig_benchmark_ssim.png', 'SSIM Comparison Across All Models and Datasets')

pn('7.1.2 State-of-the-Art Comparison')
para('We were completely shocked when our little 24M Student model hit 25.23 dB on the LOLv1 holdout set. That score is seriously competitive with major published papers. It actually nudges past Retinexformer\'s 25.16 dB. When we stacked our models in an Ensemble run, the numbers jumped even higher, landing at 29.29 dB on the LOLv2 Real tests.')

tbl(['Method','LOLv1 PSNR','LOLv2R PSNR','Params'],
    [['RetinexNet (2018)','16.77','--','0.8M'],
     ['KinD (2019)','20.87','--','8.2M'],
     ['MIRNet (2020)','24.14','--','31.8M'],
     ['Zero-DCE (2020)','14.86','--','0.08M'],
     ['SNR-Aware (2022)','24.61','--','39.1M'],
     ['Retinexformer (2023)','25.16','--','1.6M'],
     ['BioNAFNet Student (Ours)','25.23','28.48','24M'],
     ['BioNAFNet T40/S60 (Ours)','25.29','29.19','178M'],
     ['BioNAFNet T60/S40 (Ours)','25.23','29.29','178M']],
    'Comparison with Published State-of-the-Art Methods')

fig('fig_sota_comparison.png', 'PSNR Comparison with State-of-the-Art Methods on LOLv1')

pn('7.1.3 Knowledge Distillation Analysis')
para('The fact that the Student beat the Teacher is totally weird. Usually, when you compress an AI, it gets stupider. The Student is over 6 times smaller than the Teacher. But on LOLv1, it scored 25.23 against the Teacher\'s 24.94. After scratching our heads over this, we realized the massive Teacher was probably just memorizing the 128x128 training squares. The Student was too tiny to memorize things, so it was forced to actually learn the pattern, which made it perform better on brand new full-sized test images.')

tbl(['Metric','Teacher','Student','Ratio'],
    [['Parameters','154,380,888','23,969,016','Over 6x smaller'],
     ['File Size','2.47 GB','384 MB','Over 6x smaller'],
     ['Time to Run','188.7 ms','48.9 ms','Almost 4x faster'],
     ['Live FPS','5.3 frames','20.5 frames','Way smoother'],
     ['LOLv1 Score','24.94 dB','25.23 dB','Student wins'],
     ['LOLv2 Real','28.67 dB','28.48 dB','Teacher wins'],
     ['LOLv2 Synth','26.22 dB','25.75 dB','Teacher wins']],
    'Teacher vs Student Model Comparison')

fig('fig_model_profiles.png', 'Model Size vs Quality Trade-off Across All Variants')

pn('7.1.4 Ensemble Fusion Analysis')
para('Mashing both networks together resulted in the highest scores we ever saw on this project. By wiring them to run at the same time and averaging out the pixels (a 60% Teacher / 40% Student split), we hit 29.29 dB on LOLv2 Real. It turns out the Teacher focuses hard on tiny textural details, while the Student focuses on keeping the big sky blocks smooth. When you average them, you get the best of both worlds.')

fig('fig_ensemble_comparison.png', 'Ensemble Fusion Strategy Comparison')

pn('7.1.5 Ablation Study')
para('We wanted to prove our biological tricks actually did something, instead of just being dead code. So we ran tests where we deleted the modules one by one.')

tbl(['Configuration','LOLv1 PSNR','Change'],
    [['BioNAFNet (all 7 tricks on)','24.94','Baseline'],
     ['Removed RLIN (eye edge tech)','24.31','Lost 0.63'],
     ['Removed FAEB (wave tech)','24.52','Lost 0.42'],
     ['Removed ARFP (focus sizing)','24.71','Lost 0.23'],
     ['Removed PRCM (rod/cone curves)','24.78','Lost 0.16'],
     ['Removed SPDP (color split)','24.82','Lost 0.12'],
     ['Removed TAM (memory loop)','24.85','Lost 0.09'],
     ['Removed WFPL (shadow loss)','24.66','Lost 0.28'],
     ['Stripped totally bare (just NAFNet)','23.40','Lost 1.54']],
    'Ablation Study: Impact of Individual Biological Modules')

fig('fig_ablation.png', 'Ablation Study: Contribution of Each Biological Module')

para('RLIN was the MVP here. When we turned off the lateral inhibition edge-finder, the score tanked by 0.63 dB. The Fourier wave cleaner (FAEB) was the runner up, keeping a ton of noise out. When we turned them all off, the network became practically useless compared to the competition.')

pn('7.1.6 Speed Analysis')
tbl(['Model','Size','Wait Time','Video Frames','Good For'],
    [['Teacher','Huge','188.7 ms','5.3 FPS','Background batch jobs'],
     ['Student-693','Small','48.9 ms','20.5 FPS','Live webcam video'],
     ['Ensemble 50/50','Combined','240 ms','4.2 FPS','Trying to get High Scores'],
     ['Synergy T70/S30','Combined','310 ms','3.2 FPS','Math stuff']],
    'Inference Speed Comparison')

fig('fig_speed_quality.png', 'Speed vs Quality Trade-off: Inference Time vs PSNR')

pn('7.1.7 Training Convergence Analysis')
para('Looking at the graphs, the Teacher model tapped out early. It hit its peak score of 25.05 dB at epoch 476, and then just stopped improving. The Student model was different. When the training script finished at epoch 693, the Student\'s score graph was still pointing up. It reached 25.09 dB, but if we had left it running for a few more days, it probably would have gone even higher.')

fig('fig_teacher_convergence.png', 'Teacher Model PSNR Convergence Detail')

h3('7.2 Qualitative Results')
pn('7.2.1 Visual Comparisons')
para('We printed out the before-and-after photos to show that the AI actually knows what it is doing, instead of just scoring well on math tests. Look at the colors and edge repairs in the pictures below.')

photo('Visual comparison grid: Row 1 = LOLv1 test image #1, showing: (a) Low-light Input, (b) RetinexNet output, (c) Retinexformer output, (d) BioNAFNet Student output, (e) Ground Truth. Use images from results_student/lolv1/ folder. Description: Side-by-side comparison showing our model produces cleaner, more natural results than RetinexNet and comparable to Retinexformer.')

photo('Visual comparison grid: Row 1 = LOLv2 Real test image, showing: (a) Low-light Input, (b) Teacher output, (c) Student output, (d) Ensemble T60/S40 output, (e) Ground Truth. Use images from results_ensemble/ensemble_teacher60/ folder. Description: Show how the Ensemble combines the best of Teacher and Student for the highest quality result.')

photo('Visual comparison zoomed crops: Take a small region (e.g., text on a sign or face) from a test image and show it at 4x zoom for: Input, Student, Teacher, Ensemble, Ground Truth. Description: Demonstrate detail recovery at the pixel level.')

pn('7.2.2 NeonEnhancer Pro Application in Action')
para('Our desktop app genuinely works. You can click around, load up your bad photos, and immediately see what the AI thinks it should look like.')

photo('Screenshot of the complete enhancement workflow: (1) Images uploaded, (2) BioNAFNet Student selected, (3) GPU mode enabled, (4) Enhancement complete with gallery showing before/after. Description: Complete end-to-end demonstration of the application.')

h3('7.3 Discussion')
pn('7.3.1 Answering Research Questions')
para('RQ1: Did the human eye stuff help the AI see better? Yeah, definitely. When we shut off all the biology modules, the AI lost 1.54 dB off its total score. The edge-finder module (RLIN) alone was carrying a massive amount of the weight.')
para('RQ2: Did the compression trick work? Absolutely. The Student file is tiny compared to the Teacher, but it actually scored higher on our test set. It was a massive win.')
para('RQ3: What happens when you run them together? Pure magic. Jamming the Teacher and Student together bumped the score up to 29.29 dB, destroying either model alone.')
para('RQ4: Is it actually usable in an app? Yes. The Student model pushes over 20 frames per second, which means our webcam feed runs totally smooth inside the GUI.')

pn('7.3.2 Limitations')
para('It is not perfect. First off, we need perfectly paired dark/light photos to train it, which you can not really get easily in real life. Also, the 2.5 GB Teacher model is way too fat to put on a normal person\'s laptop. Sometimes, if the photo is literally pitch black, the AI has no idea what to do and just guesses colors randomly. Also, adding all those biology math branches definitely made the code run slower than a naked network.')

pn('7.3.3 Future Work from Results')
para('If we had more time, here is what we would do next. One, we would just leave the Student training running for another week to see how high it could score. Two, we would love to train this on unpaired GAN data so we could just scavenge random dark photos from the internet. Finally, we should probably figure out how to convert the PyTorch file into an ONNX mobile file so we could just drop this whole thing onto an Android phone.')

doc.add_page_break()
doc.save(DOC)
print(f'Part 3 complete: Chapters 6-7')
print(f'Tables: {TN[0]} | Figures: {FN[0]}')
