# OPTIC documentation

**OPTIC** (**Op**timized **T**oolbox for **I**mage-based **C**ellular analysis) is a Python toolkit for rapid and efficient semi-automated analysis of multicellular calcium imaging and related longitudinal microscopy data.

OPTIC bundles three specialized GUI applications that plug into existing pipelines (Suite2p, CaImAn, ImageJ):

| Application | Purpose | Input |
|---|---|---|
| [OpticROICuration](OpticROICuration/tutorial.md) | Classify ROIs (neurons, astrocytes, microglia, …) and inspect event-aligned traces | Suite2p `Fall.mat` or CaImAn `*.hdf5` |
| [OpticROITracking](OpticROITracking/tutorial.md) | Track ROIs across imaging sessions via image registration + Optimal Transport. Multi-session mode supports graph-based alignment and master tracking table export. | Multiple `Fall.mat` / `*.hdf5` |
| [OpticRawTracking](OpticRawTracking/tutorial.md) | Generalized ROI tracking on raw TIFF stacks. Integrates Cellpose for ROI extraction and ImageJ for bidirectional ROI exchange. | XYCT TIFF stack |

For installation and a quick start, see the [project README](https://github.com/dhino2000/optic/blob/main/README.md).

```{toctree}
:maxdepth: 2
:caption: Applications
:hidden:

OpticROICuration/tutorial
OpticROITracking/tutorial
OpticRawTracking/tutorial
```

```{toctree}
:maxdepth: 1
:caption: Reference
:hidden:

installation
references
```

## Citation

If you use OPTIC in your work, please cite:

> Fukatsu, N., Tanisumi, Y., Cheung, D., Saito, Y., Hashimoto, A., Takahashi, N., Takeda, I., Inoue, M., & Wake, H. *OPTIC: A Rapid and Efficient Semi-automated Toolbox for Multicellular Calcium Imaging Analysis.*
