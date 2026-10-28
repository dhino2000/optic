# Installation

## Requirements

- **OS**: Windows 11
- **Python**: 3.10
- **CPU**: ≥ 24 cores recommended
- **RAM**: ≥ 128 GB recommended

## 1. Install Anaconda

Install the [Anaconda distribution](https://www.anaconda.com/download/success) to prepare a Python environment.

## 2. Get the OPTIC source

Click **Download ZIP** on the [GitHub repository](https://github.com/dhino2000/optic) and extract it to a location of your choice, e.g. `C:/Users/dhino2000/optic`.

Alternatively, clone with git:

```bash
git clone https://github.com/dhino2000/optic.git
```

## 3. Create the environment

Choose one of the two methods.

### a) Create with the bundled YAML file (recommended)

```bash
cd <optic_directory>
conda env create -f optic.yml
conda activate optic
```

### b) Manual package installation

```bash
conda create -n optic python=3.10 --override-channels -c defaults
conda activate optic
```

Then install the required packages:

| Package | Version |
|---|---|
| PyQt5 | 5.15.11 |
| numpy | 1.26.4 |
| itk | 5.4.6 |
| itk-elastix | 0.25.3 |
| matplotlib | 3.10.8 |
| pot | 0.9.6 |
| scikit-image | 0.25.2 |
| cellpose[gui] | 3.1.0 |
| networkx | ≥ 3.4 |
| pandas | ≥ 2.0 |

## Windows Smart App Control

On Windows 11 with Smart App Control enabled, unsigned binaries can fail to load with `ImportError: DLL load failed ... An Application Control policy has blocked this file` (アプリケーション制御ポリシーによってこのファイルがブロックされました). To avoid this:

- Install Python from Anaconda's `defaults` channel (its binaries are code-signed), not conda-forge. Both `optic.yml` and the manual command above do this.
- Keep itk 5.4.6 / itk-elastix 0.25.3. ITK wheels are unsigned, and this is the build verified to run elastix under Smart App Control.

## GPU acceleration (Cellpose)

If you want to use Cellpose with GPU acceleration, install a CUDA-compatible PyTorch build first — see the [PyTorch official documentation](https://pytorch.org/) for the correct command for your CUDA version.

<!--
## Verify the installation

Launch any of the three applications:

```bash
python scripts/optic_roi_curation.py
python scripts/optic_roi_tracking.py
python scripts/optic_raw_tracking.py
```

A GUI window should open. If you see import errors, double-check the environment is activated and re-run the installation step.

## Downstream analysis

After analysing with these applications, additional downstream analyses may be required. See the Jupyter notebooks beginning with **"Chapter"** in the [notebook folder](https://github.com/dhino2000/optic/tree/main/notebook) for step-by-step examples.
-->