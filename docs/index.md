# OPTIC documentation

**OPTIC** (**Op**timized **T**oolbox for **I**mage-based **C**ellular analysis) is a Python toolkit for rapid and efficient semi-automated analysis of multicellular calcium imaging and related longitudinal microscopy data.

OPTIC bundles three specialized GUI applications that plug into existing pipelines (Suite2p, CaImAn, ImageJ):

| Application | Purpose | Input |
|---|---|---|
| [OpticROICuration](OpticROICuration/tutorial.md) | Classify ROIs (neurons, astrocytes, microglia, …) and inspect event-aligned traces | Suite2p `Fall.mat` or CaImAn `*.hdf5` |
| [OpticROITracking](OpticROITracking/tutorial.md) | Track ROIs across imaging sessions via image registration + Optimal Transport. Multi-session mode supports graph-based alignment and master tracking table export. | Multiple `Fall.mat` / `*.hdf5` |
| [OpticRawTracking](OpticRawTracking/tutorial.md) | Generalized ROI tracking on raw TIFF stacks. Integrates Cellpose for ROI extraction and ImageJ for bidirectional ROI exchange. | XYCT TIFF stack |

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