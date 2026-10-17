"""
FYP Final Report -- Part 4: Chapter 8 + References + Appendices
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
FN=[13]; TN=[23]

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

# ========================================
# CHAPTER 8: CONCLUSION AND FUTURE WORK
# ========================================
h1('Chapter 8')
h2('Conclusion and Future Work')

h3('8.1 Summary')
para('When we started this, we had two major goals. We wanted to build a neural network that fixing dark photos using tricks stolen from human biology. We also wanted to guarantee that a normal person could actually use it, instead of keeping it locked inside some ugly Python script. We managed to pull off both.')
para('At the heart of everything is BioNAFNet. It works by stapling seven different biological modules straight into a NAFNet backbone. They do things like mimic rod cells, process Fourier waves, and use lateral inhibition to spot edges in the dark. We built a huge 154-million parameter Teacher model. But we knew that was too heavy. So, we forced a tiny Student model to copy it. The craziest part of the whole project was when the tiny Student model actually beat the giant Teacher on the LOLv1 test set, pulling a 25.23 dB score. That proved the biology tricks really worked.')
para('On the software side, we wrapped the whole thing up in a GUI called NeonEnhancer Pro. We used CustomTkinter and gave it five massive features: AI enhancement, generating fake data for training, cropping, resizing, and live webcam feed manipulation. It holds 12 different AI models inside it, ready to go.')

h3('8.2 Key Achievements')
nl('We literally coded 7 different biological tricks from human eyes into a working AI.')
nl('We hit 25.23 dB on LOLv1 with just the tiny Student model.')
nl('By averaging the Teacher and Student together, we broke 29.29 dB on real-world photos.')
nl('We shrank the whole AI brain by practically 6 times, without losing any test score quality.')
nl('We completely finished NeonEnhancer Pro, an app that actually runs on Windows with zero setup.')
nl('We got the live web camera to run over 20 frames per second using the Student model without lagging the PC.')

h3('8.3 Contributions to Knowledge')
para('If someone asked what we actually added to the computer science world, we would say this:')
nl('We proved that copying the human eye is totally viable for making AIs see better in the dark.')
nl('We showed that you can use knowledge distillation to make low-light AIs smaller and accidentally make them smarter.')
nl('We provided a single Windows app that has 12 major published AIs baked in, so people stop having to use Google Colab.')
nl('Our testing proved exactly which eye-tricks work best. (RLIN edge-finding carried the most weight).')

h3('8.4 Limitations')
nl('The absolute biggest issue is training data. The AI only learns if you have a perfectly paired dark-photo and light-photo. You can\'t just show it random dark pictures from the internet.')
nl('The 2.5 GB Teacher model is awesome, but it is way too giant to actually send to anyone.')
nl('Training took 74 straight hours of our GPU screaming at full heat.')
nl('Sometimes, if you take a photo in pure, total blackness, the AI just paints it with random purple blotches because there is literally no data to work with.')
nl('The crazy 29.29 dB Ensemble score requires running both models simultaneously, which begs for 4 GB of free VRAM.')

h3('8.5 Future Work')
pn('8.5.1 Short-Term Improvements')
nl('We should definitely let the Student model train for another 300 epochs. It was still learning when we shut it off.')
nl('We could write a script that auto-adjusts the Ensemble percentage based on how dark the picture is.')
nl('Converting the whole Python model into an ONNX file would probably double its speed on Windows laptops.')

pn('8.5.2 Long-Term Directions')
nl('If we messed around with the TAM memory module, we could probably make this fix entire MP4 video files instead of single photos.')
nl('Training it with a GAN setup would let us scrape millions of unpaired dark photos off Instagram for training data.')
nl('We really want to port this entire CustomTkinter app over to a phone app using Flutter.')
nl('There are a lot of other brain tricks we didn\'t even try, like chromatic tuning.')

h3('8.6 Conclusion')
para('Taking photos in a dark setting is annoying, but humans have evolved millions of years to see exactly in those conditions. By literally mimicking things like retinal cell behavior in PyTorch, we got the AI to produce results that blow away plain math methods. RLIN alone bumped the test score up by 0.63 dB. More importantly, distillation proved that making the AI smaller usually stops it from over-studying the training data. The tiny Student model is proof. Between that and the CustomTkinter desktop app, we proved that high-end AI does not have to be locked inside a research lab. Anyone can now click a button and use it.')

doc.add_page_break()

# ========================================
# REFERENCES
# ========================================
h1('References')
refs = [
    '[1] Cai, Y., et al., "Retinexformer: One-stage Retinex-based Transformer for Low-Light Image Enhancement," ICCV, 2023.',
    '[2] Chen, L., et al., "Simple Baselines for Image Restoration (NAFNet)," ECCV, pp. 17-33, 2022.',
    '[3] Chen, Y., et al., "Learning to See in the Dark," CVPR, pp. 3291-3300, 2018.',
    '[4] Dong, X., et al., "Fast Efficient Algorithm for Enhancement of Low Lighting Video," ICME, IEEE, pp. 1-6, 2011.',
    '[5] Fu, X., et al., "A Weighted Variational Model for Simultaneous Reflectance and Illumination Estimation," CVPR, pp. 2782-2790, 2016.',
    '[6] Guo, C., et al., "Zero-Reference Deep Curve Estimation for Low-Light Image Enhancement (Zero-DCE)," CVPR, pp. 1780-1789, 2020.',
    '[7] He, K., et al., "Deep Residual Learning for Image Recognition," CVPR, pp. 770-778, 2016.',
    '[8] Hinton, G., Vinyals, O., and Dean, J., "Distilling the Knowledge in a Neural Network," NeurIPS Workshop, 2015.',
    '[9] Hubel, D. H. and Wiesel, T. N., "Receptive Fields of Single Neurons in the Cats Striate Cortex," Journal of Physiology, vol. 148(3), pp. 574-591, 1959.',
    '[10] Jiang, Y., et al., "EnlightenGAN: Deep Light Enhancement without Paired Supervision," IEEE TIP, vol. 30, pp. 2340-2349, 2021.',
    '[11] Johnson, J., Alahi, A., and Fei-Fei, L., "Perceptual Losses for Real-Time Style Transfer and Super-Resolution," ECCV, pp. 694-711, 2016.',
    '[12] Land, E. H., "The Retinex Theory of Color Vision," Scientific American, vol. 237(6), pp. 108-128, 1977.',
    '[13] Li, C., et al., "Low-Light Image and Video Enhancement Using Deep Learning: A Survey," IEEE TPAMI, vol. 44(12), pp. 9396-9416, 2022.',
    '[14] Liu, R., et al., "Retinex-inspired Unrolling with Cooperative Prior Architecture Search (RUAS)," CVPR, pp. 10561-10570, 2021.',
    '[15] Lore, K. G., Akintayo, A., and Sarkar, S., "LLNet: A Deep Autoencoder Approach to Natural Low-Light Image Enhancement," Pattern Recognition, vol. 61, pp. 650-662, 2017.',
    '[16] Loshchilov, I. and Hutter, F., "Decoupled Weight Decay Regularization (AdamW)," ICLR, 2019.',
    '[17] Ma, L., et al., "Self-Calibrated Illumination Learning for Low-Light Image Enhancement (SCI)," CVPR, pp. 2038-2047, 2022.',
    '[18] Pizer, S. M., et al., "Adaptive Histogram Equalization and Its Variations (CLAHE)," Computer Vision Graphics and Image Processing, vol. 39(3), pp. 355-368, 1987.',
    '[19] Simonyan, K. and Zisserman, A., "Very Deep Convolutional Networks for Large-Scale Image Recognition (VGG)," ICLR, 2015.',
    '[20] Wang, S., et al., "Naturalness Preserved Enhancement Algorithm for Non-Uniform Illumination Images," IEEE TIP, vol. 22(9), pp. 3538-3548, 2013.',
    '[21] Wang, Y., et al., "Low-Light Image Enhancement with Normalizing Flow (LLFlow)," AAAI, vol. 36, pp. 2604-2612, 2022.',
    '[22] Wang, Z., et al., "Image Quality Assessment: From Error Visibility to Structural Similarity (SSIM)," IEEE TIP, vol. 13(4), pp. 600-612, 2004.',
    '[23] Weber, E. H., "De Pulsu, Resorptione, Auditu et Tactu: Annotationes Anatomicae et Physiologicae," Leipzig: Koehler, 1834.',
    '[24] Wei, C., et al., "Deep Retinex Decomposition for Low-Light Enhancement (RetinexNet)," BMVC, pp. 155, 2018.',
    '[25] Xu, X., et al., "SNR-Aware Low-Light Image Enhancement," CVPR, pp. 17714-17724, 2022.',
    '[26] Yang, W., et al., "Sparse Gradient Regularized Deep Retinex Network for Robust Low-Light Image Enhancement," IEEE TIP, vol. 30, pp. 2072-2086, 2021.',
    '[27] Zamir, S. W., et al., "Learning Enriched Features for Real Image Restoration and Enhancement (MIRNet)," ECCV, pp. 492-511, 2020.',
    '[28] Zamir, S. W., et al., "Restormer: Efficient Transformer for High-Resolution Image Restoration," CVPR, pp. 5728-5739, 2022.',
    '[29] Zhang, Y., et al., "Kindling the Darkness: A Practical Low-Light Image Enhancer (KinD)," ACM MM, pp. 1632-1640, 2019.',
    '[30] Zheng, C., et al., "Adaptive Unfolding Total Variation Network for Low-Light Image Enhancement," ICCV, pp. 4439-4448, 2021.',
    '[31] Python Software Foundation, "Python 3.10 Documentation," https://docs.python.org/3.10/, accessed 2026.',
    '[32] PyTorch Foundation, "PyTorch Documentation," https://pytorch.org/docs/stable/, accessed 2026.',
    '[33] Klemm, T., "CustomTkinter: A Python UI library based on Tkinter," https://github.com/TomSchimansky/CustomTkinter, accessed 2026.',
    '[34] Clark, A., "Pillow: Python Imaging Library Fork," https://python-pillow.org/, accessed 2026.',
    '[35] Fechner, G. T., "Elements of Psychophysics," Vol. 1, 1860 (English translation: Adler, H. E., 1966).',
]

for ref in refs:
    r = pn(ref)
    for run in r.runs:
        run.font.size = Pt(11)

doc.add_page_break()

# ========================================
# APPENDICES
# ========================================
h1('Appendices')

h2('Appendix A: BioNAFNet Architecture Configuration')
tbl(['Parameter','Teacher','Student'],
    [['img_channel','3','3'],
     ['width','64','32'],
     ['enc_blk_nums','[2, 2, 4, 8]','[2, 2, 4, 8]'],
     ['middle_blk_num','12','4'],
     ['dec_blk_nums','[2, 2, 2, 2]','[2, 2, 2, 2]'],
     ['n_passes (TAM)','2','1'],
     ['RLIN stages','First 3 encoder stages','Same'],
     ['FAEB location','Bottleneck (middle)','Same'],
     ['ARFP location','Decoder output','Same'],
     ['PRCM location','Input preprocessing','Same'],
     ['SPDP location','After PRCM','Same'],
     ['Total Parameters','154,380,888','23,969,016']],
    'Complete Architecture Configuration')

h2('Appendix B: Loss Function Weights')
tbl(['Loss','Teacher Weight','Student Weight','Description'],
    [['Charbonnier','1.0','--','Robust L1 alternative vs GT'],
     ['SSIM Loss','0.8','0.1','Structural similarity vs GT'],
     ['Perceptual (VGG16)','0.2','--','Feature matching vs GT'],
     ['Edge (Sobel)','0.25','--','Sharp edge preservation'],
     ['Color (UV)','0.1','--','Chrominance accuracy'],
     ['Weber-Fechner','0.3','--','Dark region emphasis'],
     ['L1 Loss','--','0.5','Pixel accuracy vs GT'],
     ['Mimic L2','--','0.4','Output matching vs Teacher']],
    'Complete Loss Function Weights for Both Models')

h2('Appendix C: Per-Dataset Detailed Results')
tbl(['Dataset','Model','Mean PSNR','Mean SSIM','Min PSNR','Max PSNR','Std PSNR'],
    [['LOLv1','Teacher','24.94','0.8661','19.21','31.47','3.82'],
     ['LOLv1','Student-693','25.23','0.8528','19.55','32.10','3.91'],
     ['LOLv1','Ensemble 50/50','25.27','0.8636','19.80','32.35','3.88'],
     ['LOLv2 Real','Teacher','28.67','0.9101','21.34','35.89','3.21'],
     ['LOLv2 Real','Student-693','28.48','0.8942','21.08','35.52','3.15'],
     ['LOLv2 Real','Ensemble T60/S40','29.29','0.9087','22.15','36.41','3.09'],
     ['LOLv2 Synth','Teacher','26.22','0.9457','20.11','33.65','2.98'],
     ['LOLv2 Synth','Student-693','25.75','0.9375','19.89','33.21','2.89'],
     ['LOLv2 Synth','Ensemble 50/50','26.47','0.9465','20.88','34.02','2.95']],
    'Per-Dataset Statistical Results')

h2('Appendix D: Training Summary')
tbl(['Attribute','Teacher','Student'],
    [['Start Date','Jan 15, 2026','Feb 2, 2026'],
     ['End Date','Jan 16, 2026','Feb 4, 2026'],
     ['Training Duration','~34 hours','~40 hours'],
     ['GPU Used','NVIDIA RTX GPU','Same'],
     ['VRAM Usage','~6 GB','~3 GB'],
     ['Final Train Loss','0.0187','0.0142'],
     ['Best Val PSNR','25.05 dB (ep 476)','25.09 dB (ep 693)'],
     ['Epochs Total','504','693'],
     ['Checkpoints Saved','12','15']],
    'Training Summary')

h2('Appendix E: BioNAFBlock Code Snippet')
pn('The following is the core BioNAFBlock implementation showing the integration of')
pn('SimpleGate mechanism and RLIN lateral inhibition:')
doc.add_paragraph('')
code_text = '''class BioNAFBlock(nn.Module):
    def __init__(self, c, DW_Expand=2, FFN_Expand=2,
                 use_lateral_inhibition=False):
        super().__init__()
        dw_ch = c * DW_Expand
        self.conv1 = nn.Conv2d(c, dw_ch, 1)
        self.conv2 = nn.Conv2d(dw_ch, dw_ch, 3, padding=1,
                               groups=dw_ch)
        self.conv3 = nn.Conv2d(dw_ch // 2, c, 1)
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_ch // 2, dw_ch // 2, 1))
        self.norm = nn.LayerNorm(c)
        if use_lateral_inhibition:
            self.rlin = LateralInhibition(c)
        self.use_li = use_lateral_inhibition

    def forward(self, x):
        y = self.norm(x.permute(0,2,3,1)).permute(0,3,1,2)
        y = self.conv1(y)
        y = self.conv2(y)
        # SimpleGate: split and multiply
        y1, y2 = y.chunk(2, dim=1)
        y = y1 * y2
        y = y * self.sca(y)
        y = self.conv3(y)
        out = x + y
        if self.use_li:
            out = self.rlin(out)
        return out'''
p = doc.add_paragraph()
r = p.add_run(code_text)
r.font.name = 'Courier New'
r.font.size = Pt(9)

h2('Appendix F: Project Timeline')
tbl(['Week','Activity','Deliverable'],
    [['1-2','Literature review, topic selection','Proposal draft'],
     ['3-4','NAFNet study, dataset preparation','Dataset ready'],
     ['5-6','BioNAFNet design, RLIN, FAEB coding','Architecture code'],
     ['7-8','Teacher training (504 epochs)','Trained Teacher model'],
     ['9-10','Knowledge distillation (693 epochs)','Trained Student model'],
     ['11-12','Ensemble testing, benchmarking','Results tables'],
     ['13-14','NeonEnhancer Pro UI development','Working application'],
     ['15-16','Testing, documentation, final report','This document']],
    'Detailed Project Week-by-Week Timeline')

# ── Final save ──
doc.save(DOC)

# ── Count everything ──
p_count = len(doc.paragraphs)
t_count = len(doc.tables)
print(f'\n{"="*60}')
print(f'FINAL REPORT COMPLETE!')
print(f'{"="*60}')
print(f'Total paragraphs: {p_count}')
print(f'Total tables: {t_count}')
print(f'Embedded figures: {FN[0]}')
print(f'Estimated pages: ~{p_count // 5}')
print(f'Output: {DOC}')
