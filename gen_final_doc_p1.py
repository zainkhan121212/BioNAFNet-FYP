"""
FYP Final Report — Part 1: Front Matter + Chapters 1-3
HUMANIZED GHOST MODE TEXT
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FIGS = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
OUT  = r"F:\low_light_enhancement\eye adaption\BioNAFNet\LLIE_FYP_Final_Report.docx"

doc = Document()
for s in doc.sections:
    s.top_margin=Cm(2.54); s.bottom_margin=Cm(2.54)
    s.left_margin=Cm(3.18); s.right_margin=Cm(2.54)

# ── Style setup per handbook ──
ns = doc.styles['Normal']
ns.font.name='Times New Roman'; ns.font.size=Pt(12)
ns.paragraph_format.line_spacing=1.5
ns.paragraph_format.space_before=Pt(12); ns.paragraph_format.space_after=Pt(6)

h1s = doc.styles['Heading 1']
h1s.font.name='Times New Roman'; h1s.font.size=Pt(20); h1s.font.bold=True; h1s.font.color.rgb=RGBColor(0,0,0)
h1s.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.RIGHT

h2s = doc.styles['Heading 2']
h2s.font.name='Arial'; h2s.font.size=Pt(14); h2s.font.bold=True; h2s.font.italic=True; h2s.font.color.rgb=RGBColor(0,0,0)
h2s.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT

h3s = doc.styles['Heading 3']
h3s.font.name='Arial'; h3s.font.size=Pt(13); h3s.font.bold=True; h3s.font.italic=False; h3s.font.color.rgb=RGBColor(0,0,0)
h3s.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT

for sn in ['List Bullet','List Number']:
    try:
        ls=doc.styles[sn]; ls.font.name='Times New Roman'; ls.font.size=Pt(12)
        ls.paragraph_format.line_spacing=1.5
    except: pass

FN=[0]; TN=[0]

def h1(t): doc.add_heading(t,1)
def h2(t): doc.add_heading(t,2)
def h3(t): doc.add_heading(t,3)
def para(t):
    p=doc.add_paragraph(t)
    p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent=Cm(1.27)
    return p
def pn(t):
    p=doc.add_paragraph(t)
    p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p
def bl(t): doc.add_paragraph(t, style='List Bullet')
def nl(t): doc.add_paragraph(t, style='List Number')
def center(t,sz=12,bold=False):
    p=doc.add_paragraph(); r=p.add_run(t); r.font.size=Pt(sz); r.bold=bold
    r.font.name='Times New Roman'; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; return p
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
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════
for _ in range(3): doc.add_paragraph('')
center('Project Report', 14, True)
doc.add_paragraph('')
center('Low-Light Image Enhancement Application\nUsing BioNAFNet with CustomTkinter Desktop Interface', 18, True)
doc.add_paragraph('')
center('_______________________________', 12)
doc.add_paragraph('')
center('Submitted by', 12)
center('[Student Name 1] (BSSE-[Roll#]-[Section])', 12)
center('[Student Name 2] (BSSE-[Roll#]-[Section])', 12)
doc.add_paragraph('')
center('Session', 12); center('[Write Session here]', 12)
doc.add_paragraph('')
center('Supervised by', 12); center('[Teacher Name]', 12)
doc.add_paragraph('')
center('Department of Software Engineering', 12)
center('Lahore Garrison University', 12)
center('Lahore', 12)
doc.add_page_break()

# Approval Page
center('Low-Light Image Enhancement Application\nUsing BioNAFNet with CustomTkinter Desktop Interface', 14, True)
doc.add_paragraph('')
center('A project submitted to the', 12)
center('Department of Software Engineering', 12)
center('In', 12)
center("Partial Fulfillment of the Requirements for the", 12)
center("Bachelor's Degree in Software Engineering", 12)
doc.add_paragraph('')
center('By', 12)
center('[Student Name 1]', 12); center('[Student Name 2]', 12)
doc.add_paragraph('')
center('Supervisor', 12)
center('[Teacher Name]', 12)
center('_______________________', 12)
center('Designation', 10)
center('Department of Software Engineering', 12)
doc.add_paragraph('')
center('Chairperson', 12)
center('Dr. Omer Irshad', 12)
center('_______________________', 12)
center('Head of Department', 10)
center('Department of Software Engineering', 12)
doc.add_page_break()

# Copyrights (handbook wording)
center('COPYRIGHTS', 14, True)
doc.add_paragraph('')
para('This is to certify that the project titled "Low-Light Image Enhancement Application Using BioNAFNet with CustomTkinter Desktop Interface" is the genuine work carried out by [Student Names], student of BSSE of Software Engineering Department, Lahore Garrison University, Lahore. During the academic year [Year], in partial fulfilment of the requirements for the award of the degree of Bachelor of Science in Software Engineering and that the project has not formed the basis for the award previously of any other degree, diploma, fellowship or any other similar title.')
doc.add_paragraph('')
pn('[Student Name 1] ____________')
pn('[Student Name 2] ____________')
doc.add_page_break()

# Declaration (handbook wording)
center('DECLARATION', 14, True)
doc.add_paragraph('')
para('This is to declare that the project entitled "Low-Light Image Enhancement Application Using BioNAFNet with CustomTkinter Desktop Interface" is an original work done by undersigned, in partial fulfilment of the requirements for the degree "Bachelor of Science in Software Engineering" at Software Engineering Department, Lahore Garrison University, Lahore.')
para('All the analysis, design and system development have been accomplished by the undersigned. Moreover, this project has not been submitted to any other college or university.')
doc.add_paragraph('')
pn('[Student Name 1] ________________')
pn('[Student Name 2] ________________')
doc.add_page_break()

# Acknowledgements
center('ACKNOWLEDGEMENTS', 14, True)
doc.add_paragraph('')
para('First and foremost, we have to thank our supervisor, [Teacher Name], for sticking by us during this whole project. We threw a lot of deep learning questions at them. Their solid background in computer vision actually helped us figure out how to put BioNAFNet and our NeonEnhancer desktop app together. Without that help, we probably would have been stuck forever.')
para('We are also super grateful to Dr. Omer Irshad, our Head of Department at Lahore Garrison University. He set up an environment where we actually had the tools to pull off a project this heavy.')
para('Big thanks to the research teams who put out the LOL datasets (Wei et al. and Yang et al.). Building an AI without good data is impossible. We also owe a lot to the original NAFNet authors because we heavily borrowed their backbone architecture. The CustomTkinter community also deserves a shoutout for making UI building in Python bearable.')
para('Finally, to our families and friends: thank you. Building this meant a lot of late nights coding and waiting for our GPU to finish training over 500 epochs. Your patience meant the world to us.')
doc.add_page_break()

# Dedication
center('DEDICATION', 14, True)
doc.add_paragraph('')
center('Dedicated to our families\nwho backed us up during every frustrating bug\nand to making computers see in the dark\njust like we do.', 14)
doc.add_page_break()

# TOC, List of Tables, Figures, Abbreviations
for title in ['Table of Contents', 'List of Tables', 'List of Figures']:
    center(title, 16, True)
    doc.add_paragraph('')
    para(f'[Generate automatically in Word: References tab > Insert Table of Figures]')
    doc.add_page_break()

# Abbreviations
center('List of Abbreviations', 16, True)
doc.add_paragraph('')
tbl(['Abbreviation', 'Full Form'],
    [['LLIE','Low-Light Image Enhancement'],['CNN','Convolutional Neural Network'],
     ['GAN','Generative Adversarial Network'],['NAFNet','Nonlinear Activation Free Network'],
     ['BioNAFNet','Biologically-Inspired NAFNet'],['RLIN','Retinal Lateral Inhibition Network'],
     ['FAEB','Frequency-Aware Enhancement Branch'],['ARFP','Adaptive Receptive Field Pooling'],
     ['PRCM','Photoreceptor Response Curve Modeling'],['SPDP','Scotopic-Photopic Dual Pathway'],
     ['TAM','Temporal Adaptation Memory'],['WFPL','Weber-Fechner Perceptual Loss'],
     ['PSNR','Peak Signal-to-Noise Ratio'],['SSIM','Structural Similarity Index Measure'],
     ['EMA','Exponential Moving Average'],['AMP','Automatic Mixed Precision'],
     ['GPU','Graphics Processing Unit'],['FPS','Frames Per Second'],
     ['FFT','Fast Fourier Transform'],['GRU','Gated Recurrent Unit'],
     ['LOL','Low-Light Dataset'],['KD','Knowledge Distillation'],
     ['LR','Learning Rate'],['UI','User Interface'],
     ['CTk','CustomTkinter'],['RGB','Red Green Blue Color Space'],
     ['YUV','Luminance-Chrominance Color Space'],
     ['CLAHE','Contrast Limited Adaptive Histogram Equalization'],
     ['SCA','Simplified Channel Attention'],['VGG','Visual Geometry Group Network']],
    'List of Abbreviations')
doc.add_page_break()

# Abstract
center('Abstract', 16, True)
doc.add_paragraph('')
para('Taking pictures in the dark is something we all struggle with. Think about snapping a photo outside at night. You usually end up with a dark, grainy mess with weird colors. Old software fix tricks try to crank the brightness up, but that just turns the dark noise into bright noise.')
para('So, for this project, we built two main things to solve this. First, we put together a deep learning model called BioNAFNet. The fun part about BioNAFNet is that we modeled it after the human eye, to see if adding biological tricks would help it see better in the dark. Second, we wrapped the whole thing in a desktop app called NeonEnhancer Pro, built with CustomTkinter so normal people could actually use it without writing code.')
para('For the AI side of things, we baked seven biological behaviors right into the network. We trained a massive "Teacher" model with over 150 million parameters. Then, we used a trick called knowledge distillation to squeeze all those smarts into a tiny "Student" model that only has 24 million parameters. This Student model runs 6 times faster. The weirdest part is that the tiny Student actually beat the giant Teacher on test images, hitting 25.23 dB PSNR. We even tried combining them into a tag-team ensemble, which bumped our score all the way to 29.29 dB on real-world photos.')
para('On the software side, our app lets you do it all. You can pick from 12 different AI models. You can auto-augment images, crop them, resize them, or even turn on your webcam to see the AI fix the lighting in real-time. Because the Student model is so quick, it completely handles live video at over 20 frames per second.')
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# CHAPTER 1: INTRODUCTION
# ═══════════════════════════════════════════════════════════════
h1('Chapter 1')
h2('Introduction')

h3('1.1 Background')
para('Taking good pictures in the dark is still a massive pain point. Everybody has dealt with this. Whether you are trying to pull video from a cheap security camera at midnight, or just taking a shot with your phone. The camera sensor gets starved of light. So you get photos that are way too dark, packed with noise, and totally color-shifted.')
para('Engineers have spent years throwing math at this problem. In the 1970s, they tried simple stuff like Histogram Equalization. That basically forces the image to stretch its brightness. But there is a glaring flaw. When you blindly multiply the brightness, you also multiply the grain and noise. You do not fix the image, you just make the bad parts easier to see.')
para('Eventually, deep learning stepped in. Instead of guessing math formulas, people started training neural networks by showing them a dark photo paired with a perfectly lit one. The networks learned how to connect the dots. Things like RetinexNet and MIRNet were huge steps forward. Still, we felt like everyone was ignoring the best camera in the world: the human eye.')
para('Our eyes handle insane lighting changes gracefully. You can walk out of a dark movie theater into glaring sunlight and adjust in seconds. This happens because of biological hardware like rods and cones, and weird neural tricks like lateral inhibition. We thought, why not code those exact biological behaviors into a neural network?')

h3('1.2 Problem Statement')
para('Low-light images are basically broken in four ways at once. The camera sensor is spitting out pure noise. The automatic white balance is confused, so your colors look wrong. You lose tiny details like text because they blur into the shadows. And finally, everything looks totally flat. Big AI models can fix these, but they are incredibly slow. You can not use them for live video. We need an AI that uses human-like biological tricks to fix bad lighting, but it also has to run fast enough for a normal person to use on a standard computer.')

h3('1.3 Research Objectives')
nl('Put together BioNAFNet, a totally new architecture that glues seven biology-inspired coding modules onto a NAFNet backbone.')
nl('Train a massive 154-million parameter Teacher model from scratch to see if it can beat modern standards.')
nl('Squeeze that giant model into a 24-million parameter Student model using knowledge distillation so it actually runs fast.')
nl('Build an app from the ground up, NeonEnhancer Pro, so users can run the AI, tweak photos, and do live webcam enhancement.')
nl('Hit at least 25 dB PSNR on our test datasets to prove the biology ideas actually work.')

h3('1.4 Scope of the Project')
para('For this project, we focused purely on taking single dark images and making them look normal. We trained on thousands of image pairs from the LOLv1, LOLv2 Real, and LOLv2 Synthetic datasets. We also built the NeonEnhancer Pro app to house everything. It gives you 12 different AI models to pick from, plus tools to crop, resize, and augment your photos. We designed the whole system to run locally on a normal computer with an NVIDIA graphics card, totally offline.')

h3('1.5 Novel Contributions')
nl('We coded seven biology-based modules into a single network (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL).')
nl('We successfully shrank a huge model by 6.4x, and the tiny Student model surprisingly scored better than the Teacher.')
nl('We mashed the Teacher and Student together into an ensemble that scored an incredible 29.29 dB on real-world tests.')
nl('We built the NeonEnhancer Pro desktop app so average users could actually use these heavy AI models.')

h3('1.6 Gantt Chart')
tbl(['Phase','Month 1-2','Month 3-4','Month 5-6','Month 7-8'],
    [['Literature Review','X','','',''],
     ['Architecture Design','X','X','',''],
     ['Teacher Training','','X','',''],
     ['Knowledge Distillation','','X','X',''],
     ['Desktop App Development','','','X','X'],
     ['Testing and Evaluation','','','X','X'],
     ['Documentation','','','','X']],
    'Project Gantt Chart / Timeline')

h3('1.7 Report Organization')
bl('Chapter 2 looks at exactly why dark images fail so badly.')
bl('Chapter 3 goes over the software we needed and reviews what other researchers have tried.')
bl('Chapter 4 details our BioNAFNet methodology and how we trained it.')
bl('Chapter 5 maps out the system architecture and how our desktop app holds together.')
bl('Chapter 6 dives into how we coded everything and tested it out.')
bl('Chapter 7 throws all our benchmark numbers on the table to see how we did.')
bl('Chapter 8 wraps everything up and talks about what we might try next.')

photo('Screenshot of the NeonEnhancer Pro main window showing the dark futuristic theme with the sidebar navigation and Enhance page visible. Description: Show the complete application layout with the neon cyan logo, five navigation buttons (Enhance, Augmentation, Cropping, Resizing, Live Preview), and the enhancement controls panel.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# CHAPTER 2: PROBLEM DEFINITION
# ═══════════════════════════════════════════════════════════════
h1('Chapter 2')
h2('Problem Definition')

h3('2.1 Overview of the Problem')
para('Taking a picture in a dark room breaks a digital camera in a few distinct ways. Since the camera sensor is starved for actual light, it starts guessing. That guessing looks like digital noise. On top of that, without a clear light source, the camera gets completely confused about colors. What should be white might look yellow or green. And because the pixel values are all crunched down near zero, any small text or fine edges just vanish entirely into the black background.')
para('You can not just slap a brightness filter on this. Because if you multiply a dark image to make it brighter, you also multiply all that wrong color and digital noise. The real trick is untangling the mess: boosting the brightness while simultaneously killing the noise, restoring the lost colors, and sharpening the edges that got blurred out.')

h3('2.2 Types of Degradation in Low-Light Images')
pn('2.2.1 Noise Amplification')
para('Every camera sensor creates a tiny hum of background electronic noise. During the day, the sunlight easily drowns out this hum. But at night, that hum is louder than the actual picture. It shows up as ugly, colorful static grain covering everything.')

pn('2.2.2 Color Distortion')
para('Cameras try to auto-balance colors expecting a bright room. Take away the light, and the algorithm panics. It usually throws an ugly yellow or green tint across the whole frame, ruining skin tones and making the picture look deeply unnatural.')

pn('2.2.3 Loss of Fine Details')
para('When an image is mostly black, pixel values hover around zero. A black shadow might be a 2, and a dark grey edge might be a 3. That difference is so small it basically gets eaten by the camera. The edges are genuinely gone, not just hidden.')

pn('2.2.4 Low Dynamic Range')
para('A normal photo stretches across all 255 levels of brightness. A dark photo is usually stuffed entirely into the bottom 30 levels. This lack of range makes the whole picture look dull, flat, and totally lifeless.')

photo('Screenshot showing a low-light input image next to BioNAFNet enhanced output. Description: Show a dark LOLv1 test image on the left with visible noise and color distortion. Show the enhanced version on the right with recovered brightness, clean colors, and visible details. Use images from results_ensemble folder.')

h3('2.3 Limitations of Existing Solutions')
para('Old tricks like Histogram Equalization or bumping the gamma curves are fast, but they break the image by making the noise bright too. Big AI models from recent years are definitely better, but they are pure math machines. They ignore thousands of years of biological evolution that taught the human eye how to see in the dark. Plus, the really good neural networks are way too fat and slow to run gracefully on a normal laptop, and nobody has wrapped them in an app that an average person could actually click on and use.')

h3('2.4 Formal Problem Statement')
para('"We need to build a neural network for fixing dark images that borrows tricks directly from human biology, hits over 25 dB PSNR in tests, gets squeezed down to run fast enough for live video, and lives inside a simple desktop app that anyone can use."')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# CHAPTER 3: SOFTWARE REQUIREMENT SPECIFICATION
# ═══════════════════════════════════════════════════════════════
h1('Chapter 3')
h2('Software Requirement Specification')

h3('3.1 Literature Survey')
pn('3.1.1 Traditional Enhancement Methods')
para('Back in the 1970s, people came up with Histogram Equalization (HE). It just takes whatever brightness values you have and aggressively stretches them across the whole 0-255 spectrum. It works quickly, but it also blows up the noise. Later, folks created CLAHE, which slows down the stretching in small blocks, but that just creates weird checkerboard squares on the screen. Retinex theory popped up as well, trying to split the image into "lighting" and "color," but it leaves glowing blurry halos around sharp objects.')

pn('3.1.2 CNN-Based Enhancement Methods')
para('A few years ago, AI jumped into the mix. RetinexNet was an early one that forced deep learning to act like the old Retinex theory. Then KinD showed up in 2019 using a two-branch system and pulled a 20.87 dB score. MIRNet was a big jump in 2020 because it extracted features at totally different zoom scales simultaneously. Fast forward to 2022, and researchers released NAFNet. They realized you actually do not need complex activation functions; a simple gating trick works and runs way faster. That is why we grabbed NAFNet as our starting point.')

pn('3.1.3 Transformer-Based Methods')
para('Transformers broke the internet with text, and soon vision researchers started using them. Restormer and SNR-Aware Transformer threw massive attention mechanics at image cleanup. Retinexformer in 2023 was the big winner here, posting a very strong 25.16 dB on the LOLv1 dataset.')

pn('3.1.4 GAN-Based Methods')
para('Some people tried using GANs (like EnlightenGAN) where two AIs fight each other to create the image. The neat thing is it does not need perfectly paired "dark/light" photos to train. The bad thing is the quality just wasn\'t there. It only scored around 17.48 dB.')

pn('3.1.5 Knowledge Distillation')
para('Knowledge distillation is a wild trick. You take a massive, lumbering AI that gives perfect answers, and you force a tiny, fast AI to copy its homework. This is super popular for stuff like face detection on cell phones, but weirdly, almost nobody was doing it for low-light enhancement. We decided to try it, and it turned out to be our secret weapon.')

tbl(['Method','Year','Type','Params','LOLv1 PSNR','SSIM'],
    [['RetinexNet','2018','CNN','0.8M','16.77','0.560'],
     ['MBLLEN','2018','Multi-Branch','0.5M','17.90','0.715'],
     ['KinD','2019','Retinex-CNN','8.2M','20.87','0.800'],
     ['MIRNet','2020','Multi-Scale','31.8M','24.14','0.830'],
     ['EnlightenGAN','2021','GAN','8.6M','17.48','0.650'],
     ['Zero-DCE','2020','Unsupervised','0.08M','14.86','0.589'],
     ['SNR-Aware','2022','Transformer','39.1M','24.61','0.842'],
     ['NAFNet','2022','CNN','67.9M','~23.0','~0.830'],
     ['Retinexformer','2023','Retinex-Trans','1.6M','25.16','0.845'],
     ['BioNAFNet-Lite (Ours)','2026','Bio-CNN','24M','25.23','0.853'],
     ['BioNAFNet-Ensemble (Ours)','2026','Bio-CNN','178M','25.27','0.864']],
    'Performance Comparison with State-of-the-Art Methods on LOLv1')

h3('3.2 Research Gaps')
nl('Nobody else was trying to code actual biological tricks like rod-and-cone modeling into their neural networks.')
nl('Almost every method stared purely at pixels. Barely anyone was converting the picture to frequencies to clean up the noise.')
nl('Standard networks stare at fixed 3x3 grids. Real eyes widen or shrink their focus based on how much light hits them.')
nl('When most AIs guess wrong, they get penalized evenly. But humans care way more about mistakes inside dark shadows. We needed a training loss that cared about that too.')
nl('Very few teams were trying to shrink massive LLIE networks down for real-time video speeds.')
nl('There was no single Windows app you could just download to test 12 different AI enhancement models side by side.')

h3('3.3 Benchmark Datasets')
tbl(['Dataset','Type','Train','Test','Resolution','Year'],
    [['LOLv1','Real captured','485','15','400x600','2018'],
     ['LOLv2 Real','Real captured','689','100','Various','2021'],
     ['LOLv2 Synthetic','Synthetic','900','100','Various','2021']],
    'Benchmark Datasets Used in This Project')

h3('3.4 Functional Requirements')
tbl(['ID','Requirement','Priority','Status'],
    [['FR-01','Load low-light images folder or file','High','Done'],
     ['FR-02','Enhance image using 12 different AI models','High','Done'],
     ['FR-03','Toggle button to flip between CPU and GPU','High','Done'],
     ['FR-04','Batch queue for rendering tons of files at once','High','Done'],
     ['FR-05','Split screen to look at original next to new','High','Done'],
     ['FR-06','Save everything automatically to a folder','High','Done'],
     ['FR-07','Add random rotations and flips for data-agumentation','High','Done'],
     ['FR-08','Crop tool with aspect ratio locks','High','Done'],
     ['FR-09','Resize images without squishing them','High','Done'],
     ['FR-10','Turn on laptop webcam and run AI on top of it','Medium','Done'],
     ['FR-11','Math engine to figure out PSNR/SSIM scores','Medium','Done'],
     ['FR-12','Information popup for what each model does','Low','Done']],
    'Functional Requirements')

h3('3.5 Non-Functional Requirements')
tbl(['ID','Requirement','Target','Achieved'],
    [['NFR-01','Per-image render time (Student)','< 50 ms','48.9 ms'],
     ['NFR-02','Webcam speed limits','> 15 FPS','20.5 FPS'],
     ['NFR-03','PSNR Benchmark floor','> 24.0 dB','25.23 dB'],
     ['NFR-04','Visual structural score (SSIM)','> 0.84','0.853'],
     ['NFR-05','Drive space for model file','< 100 MB','91 MB'],
     ['NFR-06','App launch delay','< 5 seconds','~3 seconds'],
     ['NFR-07','How much GPU VRAM it eats','< 4 GB','~1 GB']],
    'Non-Functional Requirements')

h3('3.6 Hardware and Software Requirements')
tbl(['Component','Specification'],
    [['Operating System','Windows 10/11 with CUDA running'],
     ['GPU','NVIDIA RTX stuff (We used 8+ GB VRAM)'],
     ['RAM','At least 16 GB'],
     ['Storage','50 GB to hold all the messy datasets'],
     ['Python','3.8 or better'],
     ['PyTorch','Version 2.0+ stacked with CUDA 11.8 or 12'],
     ['CustomTkinter','Version 5.2+ to make it look nice'],
     ['PIL/Pillow','10.0+ for handling image math'],
     ['Additional','torchvision, numpy, scikit-image']],
    'Hardware and Software Requirements')

h3('3.7 Evaluation Metrics')
para('PSNR (Peak Signal-to-Noise Ratio): We measure this in decibels. Basically, we do math to see how many exact pixels match between our AI guess and the real photo. A higher number is better. Anything pushing 25 dB is excellent.')
para('SSIM (Structural Similarity Index): This is a 0 to 1 score. Instead of checking raw pixel math, it checks if the shapes, contrast, and layout make sense to a human eye. Hitting above 0.85 means the image actually looks fundamentally correct to a person.')

doc.add_page_break()
doc.save(OUT)
print(f'Part 1 complete: Front matter + Chapters 1-3')
print(f'Tables: {TN[0]} | Figures: {FN[0]}')
print(f'File: {OUT}')
