"""Analyze AI writing patterns in BioNAFNet_Master_Report.docx"""
import zipfile, xml.etree.ElementTree as ET

docx_path = r'F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Master_Report.docx'
with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read('word/document.xml')
root = ET.fromstring(xml_content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

paragraphs = []
for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    texts = []
    for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
        for t in run.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                texts.append(t.text)
    text = ''.join(texts).strip()
    if len(text) > 60:
        paragraphs.append(text)

# Save full text
with open(r'F:\low_light_enhancement\eye adaption\BioNAFNet\master_report_text.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(paragraphs):
        f.write(f'[P{i}] {p}\n\n')

print(f'Total paragraphs: {len(paragraphs)}')

# Show 15 sample paragraphs
print('\n=== SAMPLE PARAGRAPHS ===')
for idx in [0,5,10,20,30,50,70,100,130,160,190,220,250,280,300]:
    if idx < len(paragraphs):
        print(f'\n[P{idx}] {paragraphs[idx][:250]}')

# AI pattern counts
print('\n\n=== AI WRITING PATTERNS FOUND ===')
patterns = [
    'This is', 'It is important', 'In this', 'The following',
    'Furthermore', 'Moreover', 'Additionally', 'demonstrates',
    'highlights', 'leverages', 'utilizes', 'comprehensive',
    'robust', 'significant', 'effectively', 'plays a crucial',
    'ensuring', 'facilitating', 'In summary', 'Overall',
    'In conclusion', 'designed to', 'aims to', 'serves as',
    'This chapter', 'This section', 'crucial role', 'seamlessly',
    'meticulously', 'delve', 'pivotal', 'noteworthy',
    'encompasses', 'paradigm', 'landscape', 'holistic',
    'cutting-edge', 'state-of-the-art', 'harness',
]

results = {}
for pat in patterns:
    count = sum(1 for p in paragraphs if pat.lower() in p.lower())
    if count > 0:
        results[pat] = count

for pat, count in sorted(results.items(), key=lambda x: -x[1]):
    print(f'  "{pat}" -> {count} occurrences')

# Sentence structure analysis
print('\n\n=== SENTENCE STRUCTURE ANALYSIS ===')
long_sents = 0
short_sents = 0
total_sents = 0
for p in paragraphs:
    sents = [s.strip() for s in p.replace('!','.').replace('?','.').split('.') if len(s.strip()) > 10]
    for s in sents:
        total_sents += 1
        words = len(s.split())
        if words > 30:
            long_sents += 1
        elif words < 10:
            short_sents += 1

print(f'Total sentences: {total_sents}')
print(f'Long sentences (>30 words): {long_sents} ({long_sents*100//total_sents}%)')
print(f'Short sentences (<10 words): {short_sents} ({short_sents*100//total_sents}%)')
print(f'Medium sentences: {total_sents-long_sents-short_sents} ({(total_sents-long_sents-short_sents)*100//total_sents}%)')

# Average sentence length
total_words = sum(len(s.split()) for p in paragraphs
                  for s in p.replace('!','.').replace('?','.').split('.')
                  if len(s.strip()) > 10)
avg = total_words / max(total_sents, 1)
print(f'Average sentence length: {avg:.1f} words')
print(f'\nAI FLAG: Uniform sentence length is a major AI indicator.')
print(f'Humans vary between 5 and 35 words. AI tends to stay at 18-25.')
