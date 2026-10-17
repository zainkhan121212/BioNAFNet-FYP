# BioNAFNet — Biological Novelties Unit Tests
This folder contains the standalone core biological novelties and their complete PyTorch unit test suite. You can run these tests on any computer to mathematically prove that the 7 novelties are functioning correctly.

## 📦 What's Included?
- `novels.py` — The 7 core biological novelties (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL).
- `model.py` — The assembled BioNAFNet architecture utilizing the novelties.
- `nafnet_blocks.py` — The backbone network blocks.
- `tests/` — The complete PyTest suite (12 test scripts, 57 individual tests).

## 🚀 How to Run the Tests on Any Laptop

### Step 1: Install Python and PyTorch
Ensure you have Python installed. The easiest way is using Anaconda or Miniconda.
If you have a fresh environment, you will need `torch` and `pytest`:

```bash
pip install torch torchvision
pip install pytest
```

*(Note: PyTorch can be installed in CPU-only mode for these tests. A GPU is NOT required to run the mathematical unit tests).*

### Step 2: Open Terminal / Command Prompt
Open your terminal (or Anaconda Prompt) and navigate to the directory where you extracted this zip file.

### Step 3: Run the Test Suite
Run the following command to execute all 57 checks:

```bash
python -m pytest "tests" -v
```

### What You Will See
You will see PyTest discover 57 items and run them sequentially. Every line should end in a green `PASSED`.

```text
============================= test session starts =============================
tests/test_novel1_rlin.py::TestRLIN::test_output_shape PASSED            [  1%]
...
tests/test_novel7_wfpl.py::TestWeberFechnerLoss::test_gradient_flows PASSED [100%]
============================= 57 passed in 3.00s ==============================
```

## 🔍 Specific Novelty Testing
If you want to run tests for a specific novelty (for example, during a presentation demo), just pass the exact file name:

```bash
# Test only Novelty 3: ARFP
python -m pytest "tests/test_novel3_arfp.py" -v

# Test only Novelty 6: TAM
python -m pytest "tests/test_novel6_tam.py" -v
```

These tests guarantee that the shapes, gradients, mathematical limits (no NaNs), and specific biological constraints are behaving exactly as designed!
