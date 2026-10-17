# Results, comparison, and provenance

No full benchmark or training run was performed for repository publication. This page separates report claims from the saved evaluation artifact. Do not assume the release checkpoints reproduce every table in the report.

## Master Report: Chapter 7, Tables 21 and 22

PSNR is in dB; larger PSNR and SSIM are better within the same evaluation protocol.

| Model | LOLv1 PSNR | Real PSNR | Synthetic PSNR | LOLv1 SSIM | Real SSIM | Synthetic SSIM |
|---|---:|---:|---:|---:|---:|---:|
| Teacher, 2 passes | 24.94 | 28.67 | 26.22 | 0.8661 | 0.9101 | 0.9457 |
| Student-350 | 23.44 | 26.78 | 25.06 | 0.8409 | 0.8844 | 0.9329 |
| Student-693 | 25.23 | 28.48 | 25.75 | 0.8528 | 0.8942 | 0.9375 |
| Synergy T70/S30 | 24.96 | 28.90 | 26.33 | 0.8646 | 0.9095 | 0.9472 |
| Ensemble 50/50 | 25.27 | 29.26 | 26.47 | 0.8637 | 0.9080 | 0.9462 |
| Ensemble T60/S40 | 25.23 | 29.29 | 26.46 | 0.8649 | 0.9094 | 0.9468 |

Source: [Master Report](BioNAFNet_Master_Report.pdf), PDF pages 57–61. Appendix D contains some different ensemble SSIM values; this table consistently transcribes Chapter 7 rather than mixing sources.

The reported Student-693 has 6.44 times fewer parameters, +0.29 dB LOLv1 PSNR, and lower SSIM than the teacher. The report gives 188.7 ms / 5.3 FPS for the teacher and 48.9 ms / 20.5 FPS for the student. These timings lack a sufficiently precise GPU/resolution/protocol specification for independent reproduction; they are not performance promises for another computer. TAM aggregation is bypassed for one-pass inference.

## Saved evaluation CSV

The original [eval_summary_teacher_student.csv](eval_summary_teacher_student.csv) records:

| Model | Dataset | PSNR | SSIM | Recorded time_s |
|---|---|---:|---:|---:|
| Teacher | LOLv1 | 25.0457 | 0.8655 | 8.0 |
| Teacher | LOLv2 Real | 27.9596 | 0.9092 | 32.5 |
| Teacher | LOLv2 Synthetic | 26.2216 | 0.9457 | 23.0 |
| Student | LOLv1 | 25.0921 | 0.8517 | 4.2 |
| Student | LOLv2 Real | 27.7854 | 0.8930 | 15.0 |
| Student | LOLv2 Synthetic | 25.7527 | 0.9375 | 12.3 |

The CSV has no checkpoint hashes or complete run metadata. Its `time_s` column must not be interpreted as per-image latency or used to derive the report's FPS. Differences may reflect checkpoints or evaluation settings; the cause is unverified.

## Comparisons with other methods

The report's Table 23 lists LOLv1 PSNR / SSIM as 16.77 / 0.560 for RetinexNet, 20.87 / 0.800 for KinD, 24.14 / 0.830 for MIRNet, and 25.16 / 0.845 for Retinexformer. These are report-transcribed literature comparisons, not methods rerun under a controlled shared protocol. The report's reference list supplies the cited papers. No current state-of-the-art ranking is claimed here.

## Ablations and limitations

Checkpoint inspection found that `Student_Model/checkpoints/student_693_best_student.pth` actually stores epoch 350 (validation PSNR 23.7088). The published student instead comes from `Student_Model/checkpoints/best.pth`, which stores epoch 693 (validation PSNR 25.0921). The teacher checkpoint stores epoch 476 (validation PSNR 25.0457). Validation metadata is not interchangeable with full-resolution test-set results. The release manifest records the selected sources and hashes.

The report explicitly states on PDF pages 65 and 67 that its module ablations were estimated instead of measured by retraining separate variants. Tables 26 and 27 also use different baselines. Their numbers must not be presented as experimental proof of each module's gain. The original report is preserved unchanged for provenance.

Other limitations include 128x128 training patches, limited benchmark datasets, and unverified generalization to arbitrary camera noise and extreme darkness. The report's 589 MB / 91 MB model-size comparison describes approximately inference-only tensors; full local training checkpoints are much larger because they include training state. Release manifests give actual exported byte sizes and metadata.
