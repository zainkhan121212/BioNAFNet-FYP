"""
FYP Final Report — Part 2: Chapters 4-5 (Methodology + System Architecture)
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
FN=[0]; TN=[7]

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
# CHAPTER 4: METHODOLOGY
# ═══════════════════════════════════════════════════════════════
h1('Chapter 4')
h2('Methodology')

h3('4.1 Research Approach')
para('We tackled this project in four big chunks. First, we had to figure out how to write the Python code for our seven biology-inspired ideas and stick them into a working neural network. Second, we trained a massive 154-million parameter version of that network (we call it the Teacher) on about two thousand image pairs. It took a long time. Third, we ran a distillation process to cram all that learned knowledge into a smaller 24-million parameter Student version. Finally, we took all those trained models and wrapped them in a completely custom desktop GUI so people could actually use them without knowing how to code.')
nl('Phase 1 - Architecture Design: Building the code for the biology modules and testing if they work.')
nl('Phase 2 - Teacher Training: The heavy lifting where the big model trained for 504 epochs.')
nl('Phase 3 - Knowledge Distillation: Squeezing the Teacher so we got a Student model that runs fast.')
nl('Phase 4 - Application Development: Building the NeonEnhancer Pro app using CustomTkinter.')

h3('4.2 NAFNet Backbone')
para('We did not want to reinvent the wheel, so we used NAFNet as our foundation. The cool thing about NAFNet is that it rips out standard activation functions like ReLU. Normally, ReLU just deletes negative numbers, which means you lose a bunch of image data. Instead, NAFNet uses a trick called SimpleGate: it splits the data in half and multiplies the halves together. It is surprisingly simple but works amazingly well.')
para('Inside the network, it does a few things in order. It normalizes the data, expands it, runs a spatial convolution to look at picture shapes, applies the SimpleGate trick, adjusts the channels with attention, and shrinks it back down. We named our mutated version BioNAFBlock, mainly because we wedge our own custom biology code (like the lateral inhibition module) right into the middle of it.')

h3('4.3 Module 1: RLIN (Retinal Lateral Inhibition Network)')
para('Consider how your retina actually works. A cell in the middle gets excited by light, but the cells surrounding it actually try to turn it off. This creates a weird push-pull effect that makes sharp edges pop out aggressively. That is exactly why you can spot the outline of a doorway inside a pitch-black room.')
para('To make the AI do this, we built RLIN. We split the data into two paths. The first path is the "center" — just a normal 1x1 convolution reading the direct pixel. The second path is the "surround" — we blur a 5x5 chunk of pixels to see what the neighborhood is doing. Then, we just subtract the neighborhood from the center pixel and scale it by a trainable number. We shoved this into every block in the early part of the network.')

photo('Diagram of RLIN module showing the center pathway (1x1 conv) and surround pathway (5x5 AvgPool + 1x1 conv) with subtraction and scaling. Draw in PowerPoint with arrows showing the data flow.')

h3('4.4 Module 2: FAEB (Frequency-Aware Enhancement Branch)')
para('Your brain also looks at pictures in terms of frequencies. Fine details are high frequency. Big blobs of color are low frequency. Digital noise completely wrecks high frequencies in dark images.')
para('We built FAEB to sit right at the deepest part of the network. It literally runs a Fast Fourier Transform on the image data, splitting it into wave frequencies instead of pixels. It cleans up those waves, and then runs an inverse transform to turn it back into a normal picture. We had to force this part to run in 32-bit float math, because whenever we tried it in 16-bit, the math blew up and crashed our training loop.')

h3('4.5 Module 3: ARFP (Adaptive Receptive Field Pooling)')
para('In daylight, your eyes use cone cells which focus on tiny, sharp points. But at night, your rod cells take over, and they group together to suck in light from a wider area. You lose sharpness, but you gain brightness.')
para('We copied this behavior with ARFP. We set up three different convolution sizes: 3x3 (small cone focus), 5x5, and 7x7 (wide rod focus). Then we gave the network a gate that looks at how dark the picture is. If it is pitch black, it cranks up the 7x7 focus to gather more light. If there is a bright streetlamp in the corner, it switches that spot to 3x3 for sharp detail. This sits right at the end of the network.')

h3('4.6 Module 4: PRCM (Photoreceptor Response Curve Modeling)')
para('Rod cells actually respond to light differently than cone cells on a mathematical level. Rods are extremely sensitive to the tiniest glow in the dark, while cones care more about bright daylight.')
para('We made PRCM to mimic this. It takes the raw, dark input image and runs it through two different math curves. One curve simulates rod cells, making dark things wildly brighter. The other acts like cone cells, keeping things normal. A sigmoid math function acts like the brain, smoothly blending the two pictures together based on the lighting. We put this right at the front door of the network before anything else happens.')

h3('4.7 Module 5: SPDP (Scotopic-Photopic Dual Pathway)')
para('Human vision literally wires brightness and color through two separate cables in your head. One path is just watching for brightness and movement, while the other stares at color and fine details.')
para('We coded SPDP to split the image into YUV color space. The Y channel is just pure brightness. U and V handle the color. We built two separate mini-networks. One fixes the brightness map, and the other untangles the messy colors. Right after the PRCM module finishes, SPDP jumps in, splits the channels, cleans them separately, and glues them back together.')

h3('4.8 Module 6: TAM (Temporal Adaptation Memory)')
para('Step out of the sun into a dark basement, and you are totally blind. Wait five minutes, and you can see fine. That is dark adaptation. No other AI we looked at even tried to copy this time delay behavior.')
para('We built TAM using a GRU memory cell. We force the image through the Teacher network twice. The first pass does a rough cleanup. The GRU remembers what it saw, holds onto that memory, and uses it to help the second pass get things perfectly right. We ended up turning this off for the Student model because running it twice made it too slow for live webcam video.')

h3('4.9 Module 7: WFPL (Weber-Fechner Perceptual Loss)')
para('There is an old biology rule called the Weber-Fechner law. It proves that humans care way more about errors in shadows than errors in bright light. If a dark shadow shifts slightly, you notice it blocky artifacts instantly. If a bright sky shifts, you do not care.')
para('We wrote WFPL as a custom loss function. It looks at the picture and creates a weight map. It slaps massive math penalties on the AI if it messes up the dark pixels, but gives it a pass if it makes a tiny mistake in the bright parts. This forced the AI to stop hiding its noise in the shadows.')

h3('4.10 Complete Loss Function')
tbl(['Loss Component','Weight','Purpose'],
    [['Charbonnier','1.0','Basic pixel math testing'],
     ['SSIM','0.8','Making sure shapes look normal to a human'],
     ['Perceptual (VGG16)','0.2','Matching deep AI features'],
     ['Edge (Sobel)','0.25','Keeping lines and text sharp'],
     ['Color (UV channels)','0.1','Fixing the ugly green tint'],
     ['Weber-Fechner','0.3','Punishing mistakes in the shadows']],
    'Teacher Model Loss Function Components')

tbl(['Loss Component','Weight','Purpose'],
    [['L1 (vs ground truth)','0.5','Basic pixel checks'],
     ['SSIM (vs ground truth)','0.1','Checking image shapes'],
     ['Mimic L2 (vs teacher)','0.4','Forcing Student to cheat off Teacher']],
    'Student Model Distillation Loss Components')

h3('4.11 Training Configuration')
tbl(['Parameter','Teacher','Student'],
    [['Architecture','Huge (width=64, 2-pass)','Tiny (width=32, 1-pass)'],
     ['Parameters','154,380,888 (154M)','23,969,016 (24M)'],
     ['Optimizer','AdamW','AdamW'],
     ['Initial LR','2e-4','2e-4'],
     ['LR Scheduler','Cosine wave setup','Same'],
     ['Batch Size','4 (we faked 8 to save RAM)','4'],
     ['Gradient Clipping','0.5','0.5'],
     ['Patch Size','128x128 chunks','128x128 chunks'],
     ['EMA Decay','0.9995','0.9995'],
     ['Mixed Precision','Yes (but 32-bit for FFT)','Yes'],
     ['Training Epochs','504','693'],
     ['Best Val PSNR','25.05 dB (epoch 476)','25.09 dB (epoch 693)'],
     ['Training Time','About 34 hours','About 40 hours'],
     ['Training Data','2074 pairs combined','Same + Teacher outputs']],
    'Complete Training Configuration')

h3('4.12 Knowledge Distillation')
para('Here is how we did the compression. We froze our big 154-million parameter Teacher so it could not change. Then we span up a tiny 24-million parameter Student. We fed a dark image into both of them. We told the Student, "You get a better score the closer your answer matches the Teacher\'s answer". This is basically forcing the small network to copy the big network\'s homework.')
para('The payoff was huge. The file size shrank from 589 MB down to just 91 MB. It ran almost four times faster. The craziest thing was that when we finally tested it on the LOLv1 holdout set, the Student actually scored a 25.23 dB, beating the massive Teacher\'s 24.94 dB. We suspect the smaller size actually prevented the Student from overthinking things.')

fig('fig_distillation.png', 'Knowledge Distillation Compression: Teacher (154M) vs Student (24M)', 6)

h3('4.13 Ensemble Fusion')
para('We had both models sitting there, so we figured, why not run them both at the same time and average the results? The big Teacher is great at pulling out tiny hidden details, while the Student is really aggressive about cleaning up sky noise. We wrote a quick script to blend them together at a 50/50 ratio. It slowed the whole process down, but the score on the LOLv2 Real dataset skyrocketed to an amazing 29.29 dB.')
tbl(['Strategy','Teacher %','Student %','LOLv1 PSNR','LOLv2R PSNR'],
    [['Teacher only','100','0','24.94','28.67'],
     ['Student only','0','100','25.23','28.48'],
     ['Synergy','70','30','24.96','28.90'],
     ['Ensemble 50/50','50','50','25.27','29.26'],
     ['Ensemble T60/S40','60','40','25.23','29.29'],
     ['Ensemble T40/S60','40','60','25.29','29.19']],
    'Ensemble Fusion Strategy Comparison')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# CHAPTER 5: SYSTEM ARCHITECTURE / INITIAL DESIGN
# ═══════════════════════════════════════════════════════════════
h1('Chapter 5')
h2('System Architecture / Initial Design')

h3('5.1 System Architecture')
pn('5.1.1 Architecture Design Approach')
para('We had to build two completely separate beasts. The backend is the BioNAFNet model, which is pure PyTorch math. The frontend is the NeonEnhancer Pro app, which is what the user actually sees. We kept them totally modular. If the AI breaks, the UI does not crash. If we want to drop a new neural network in later, we don\'t have to rewrite the buttons on the screen.')

pn('5.1.2 Overall Architecture')
para('We stacked the system in four layers:')
nl('Input Layer: The messy part that grabs JPEGs, forces them into the right shape, and loads them into memory.')
nl('Processing Layer: The heavy PyTorch engine that runs all our custom biology modules and crunches the pixels.')
nl('Application Layer: The CustomTkinter GUI with its five working tabs.')
nl('Output Layer: The part that saves the finished image back to your hard drive and calculates the math scores.')

photo('System architecture block diagram showing two main sections: (1) BioNAFNet Model Backend (Input -> PRCM -> SPDP -> Encoder+RLIN -> FAEB -> Decoder -> ARFP -> Output) and (2) NeonEnhancer Pro Frontend (5 tabs: Enhance, Augmentation, Cropping, Resizing, Live). Draw in PowerPoint or draw.io.')

pn('5.1.3 BioNAFNet Architecture Details')
tbl(['Stage','Teacher Config','Student Config','Resolution','Key Module'],
    [['Input Conv','3 to 64','3 to 32','HxW','--'],
     ['Encoder 1','2 BioNAFBlocks','2 BioNAFBlocks','HxW','RLIN'],
     ['Encoder 2','2 BioNAFBlocks','2 BioNAFBlocks','H/2xW/2','RLIN'],
     ['Encoder 3','4 BioNAFBlocks','4 BioNAFBlocks','H/4xW/4','RLIN'],
     ['Encoder 4','8 BioNAFBlocks','8 BioNAFBlocks','H/8xW/8','--'],
     ['Bottleneck','12 BioNAFBlocks','4 BioNAFBlocks','H/16xW/16','FAEB'],
     ['Decoder 1-4','2 blocks each','2 blocks each','H/8 to H','--'],
     ['Output','ARFP+Conv 64 to 3','ARFP+Conv 32 to 3','HxW','ARFP']],
    'BioNAFNet Layer-by-Layer Architecture')

h3('5.2 NeonEnhancer Pro Application Architecture')
pn('5.2.1 Application Overview')
para('We wanted NeonEnhancer Pro to feel like a modern hacking tool. We built it with CustomTkinter and gave it a dark theme heavily accented with neon pinks and cyans. It opens up at 1600x1000 pixels. We even threw in a math-based particle animation in the background just to make it look cool while it sits idle.')

pn('5.2.2 Application Pages')
tbl(['Page','Icon','Purpose','Key Features'],
    [['Enhance','Star','Main AI fixing area','12 models, run whole folders, view before/after'],
     ['Augmentation','Rotate','Make fake data','Generate 4 variations per image instantly'],
     ['Cropping','Scissors','Cut images down','Preset locks for 16:9 or square'],
     ['Resizing','Ruler','Shrink or grow','Lock the ratio so it does not squish'],
     ['Live Preview','Camera','Webcam test','Uses the Student model on live video']],
    'NeonEnhancer Pro Application Pages')

pn('5.2.3 Supported AI Models (12 Total)')
tbl(['Model','Type','Parameters','Source','Ground Truth'],
    [['BioNAFNet Teacher','Supervised','154M','Our model','Optional'],
     ['BioNAFNet Student','Supervised','24M','Our model (distilled)','Optional'],
     ['BioNAFNet Ensemble','Supervised','178M (both)','Our fusion model','Optional'],
     ['Zero-DCE','Unsupervised','0.08M','Guo et al., 2020','Not needed'],
     ['EnlightenGAN','Unsupervised','8.6M','Jiang et al., 2021','Not needed'],
     ['SCI','Unsupervised','~0.5M','Ma et al., 2022','Not needed'],
     ['RUAS','Unsupervised','~0.3M','Liu et al., 2021','Not needed'],
     ['Retinexformer','Supervised','1.6M','Cai et al., 2023','Optional'],
     ['MIRNet','Supervised','31.8M','Zamir et al., 2020','Optional'],
     ['RetinexNet','Supervised','0.8M','Wei et al., 2018','Optional'],
     ['KinD','Supervised','8.2M','Zhang et al., 2019','Optional'],
     ['LLFlow','Supervised','~38M','Wang et al., 2022','Optional']],
    'All 12 Supported Enhancement Models')

photo('Screenshot of the Enhance page showing the model selection dropdown expanded with all model options visible. Description: Show the left control panel with model dropdown, CPU/GPU toggle, and the "ENHANCE IMAGE" button.')

h3('5.3 Detailed System Design')
pn('5.3.1 Component Classification')
tbl(['Component','Type','Size','Purpose'],
    [['BioNAFNet','nn.Module','154M/24M','Main AI brain'],
     ['BioNAFBlock','nn.Module','~1.5M/0.4M each','The basic Lego brick we used'],
     ['LateralInhibition','nn.Module','~2K per block','Push-pull edge finding'],
     ['FrequencyBranch','nn.Module','~500K','FFT wave math'],
     ['AdaptiveReceptiveField','nn.Module','~100K','Rod/Cone zoom switching'],
     ['PhotoreceptorCurve','nn.Module','3 params','Gamma curve blending'],
     ['DualPathway','nn.Module','~50K','Splitting color from brightness'],
     ['TemporalAdaptation','nn.Module','~200K','Double-pass memory chunk'],
     ['NeonEnhancerPro','ctk.CTk','2708 lines','The big GUI script'],
     ['model_hooks','Python module','430 lines','The glue passing images to AI'],
     ['bionafnet_teacher','Python module','97 lines','Teacher launcher'],
     ['bionafnet_student','Python module','96 lines','Student launcher'],
     ['bionafnet_ensemble','Python module','46 lines','Fusion launcher']],
    'System Component Hierarchy')

pn('5.3.2 Data Flow')
para('If you click the big "Enhance Image" button on the UI, a bunch of things fire off behind the scenes.')
nl('First, the app tells the Python backend where your JPEG is located.')
nl('The backend wakes up the AI model and loads your picture as a giant matrix of math numbers.')
nl('It crushes those numbers down between 0 and 1, pads the edges so the math perfectly divides by 16, and shoots it over to the graphics card.')
nl('We turn off PyTorch gradient tracking so PyTorch knows we are just guessing, not training. This saves massive amounts of RAM.')
nl('The AI spits out a new matrix. We chop off the padded edges and convert it back to a normal color image.')
nl('Finally, we update the screen so you see the result, and we silently stash a copy in your output folder.')

pn('5.3.3 UML Diagrams')
photo('Use Case Diagram: Show User actor with use cases: Upload Image(s), Upload Folder, Select Model, Toggle CPU/GPU, Enhance Image, View Gallery, Navigate Results, Save Results, Augment Images, Crop Image, Resize Image, Live Webcam Preview. Draw in draw.io or StarUML.')

photo('Class Diagram: NeonEnhancerPro (main) contains pages: EnhancePage, AugmentationPage, CroppingPage, ResizingPage, LivePage. It uses model_hooks which calls bionafnet_teacher, bionafnet_student, bionafnet_ensemble. BioNAFNet contains BioNAFBlock, LateralInhibition, FrequencyBranch, AdaptiveReceptiveField, PhotoreceptorCurve, DualPathway, TemporalAdaptation. Draw in draw.io or StarUML.')

photo('Activity Diagram: Start -> User Opens App -> Select Page -> [If Enhance] Upload Images -> Select Model -> Select CPU/GPU -> Click Enhance -> Processing Thread Starts -> Model Inference -> Save Enhanced Image -> Show Gallery -> End. Draw in draw.io.')

photo('Sequence Diagram: User -> NeonEnhancerPro: click Enhance, NeonEnhancerPro -> Thread: _enhance_thread(), Thread -> model_hooks: run_model(path, device), model_hooks -> BioNAFNet: forward(tensor), BioNAFNet -> Thread: return PIL Image, Thread -> NeonEnhancerPro: update gallery. Draw in draw.io.')

photo('Data Flow Diagram (Level 0): External entity "User" sends images to Process "NeonEnhancer Pro System". Process uses Data Store "LOL Dataset" for ground truth. Process outputs enhanced images to Data Store "Output Directory". Draw in draw.io.')

pn('5.3.4 Pseudocode: Enhancement Pipeline')
pn('Algorithm 1: Image Enhancement')
pn('INPUT: image_path, model_name, device')
pn('1. model = load_model_cached(model_name, device)')
pn('2. img = PIL.Image.open(image_path).convert("RGB")')
pn('3. tensor = normalize_to_01(img)')
pn('4. tensor = pad_to_multiple_of_16(tensor)')
pn('5. WITH torch.no_grad():')
pn('     output = model.forward(tensor)')
pn('6. output = clamp(output, 0, 1)')
pn('7. output = crop_to_original_size(output)')
pn('8. result = convert_to_PIL(output)')
pn('9. RETURN result')

doc.add_page_break()
doc.save(DOC)
print(f'Part 2 complete: Chapters 4-5')
print(f'Tables: {TN[0]} | Figures: {FN[0]}')
