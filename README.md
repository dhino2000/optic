# OPTIC
OPTIC(OPtimized Tools for Image-based Cellular analysis)

## Installation

1. Environment settings
Anaconda環境の作り方を書く。

(ex) conda env create -f "optic.yaml"

2. Install optic package

<img src="images/download_zip.png">

- Click on the "Download ZIP" button and extract the contents of the downloaded file
- Move the extracted folder to the appropriate directory.

(ex) "C:/Users/dhino2000/optic"

## How to use
### Suite2pROICheck
1. Open the Anaconda Prompt and switch to the desired environment.
- activate {env_name}
  
2. Execute the "suite2p_roi_check.py" script
- python {path_of_suite2p_roi_check.py}

(ex) python C:/Users/dhino2000/optic/scripts/suite2p_roi_check.py

3. Sort and Check ROIs!
([Suite2pROICheck Tutorial](https://github.com/dhino2000/optic/blob/main/docs/Suite2pROICheck/tutorial.md))

### Suite2pROITracking
([Suite2pROITracking Tutorial](https://github.com/dhino2000/optic/blob/main/docs/Suite2pROITracking/tutorial.md))

### MicrogliaTracking
([MicrogliaTracking Tutorial](https://github.com/dhino2000/optic/blob/main/docs/MicrogliaTracking/tutorial.md))

### TIFStackExplorer


## Dependencies and External Libraries

This project includes the following external libraries:

### ITKElastix

- Original Repository: https://github.com/InsightSoftwareConsortium/ITKElastix

### POT (Python Optimal Transport)

- Original Repository: https://github.com/PythonOT/POT

```bibtex
@article{flamary2021pot,
  author  = {R{\'e}mi Flamary and Nicolas Courty and Alexandre Gramfort and Mokhtar Z. Alaya and Aur{\'e}lie Boisbunon and Stanislas Chambon and Laetitia Chapel and Adrien Corenflos and Kilian Fatras and Nemo Fournier and L{\'e}o Gautheron and Nathalie T.H. Gayraud and Hicham Janati and Alain Rakotomamonjy and Ievgen Redko and Antoine Rolet and Antony Schutz and Vivien Seguy and Danica J. Sutherland and Romain Tavenard and Alexander Tong and Titouan Vayer},
  title   = {POT: Python Optimal Transport},
  journal = {Journal of Machine Learning Research},
  year    = {2021},
  volume  = {22},
  number  = {78},
  pages   = {1-8},
  url     = {http://jmlr.org/papers/v22/20-451.html}
}
```

### FGW (Fused Gromov-Wasserstein)

- Original Repository: https://github.com/tvayer/FGW

```bibtex
@InProceedings{vay2019fgw,
  title      =    {Optimal Transport for structured data with application on graphs},
  author     =    {Titouan, Vayer and Courty, Nicolas and Tavenard, Romain and Laetitia, Chapel and Flamary, R{\'e}mi},
  booktitle  =    {Proceedings of the 36th International Conference on Machine Learning},
  pages      =    {6275--6284},
  year       =    {2019},
  editor     =    {Chaudhuri, Kamalika and Salakhutdinov, Ruslan},
  volume     =    {97},
  series     =    {Proceedings of Machine Learning Research},
  address    =    {Long Beach, California, USA},
  month      =    {09--15 Jun},
  publisher  =    {PMLR},
  pdf        =    {http://proceedings.mlr.press/v97/titouan19a/titouan19a.pdf},
  url        =    {http://proceedings.mlr.press/v97/titouan19a.html}
}
```

## References
[1] S. Klein, M. Staring, K. Murphy, M.A. Viergever, J.P.W. Pluim, "elastix: a toolbox for intensity based medical image registration," IEEE Transactions on Medical Imaging, vol. 29, no. 1, pp. 196 - 205, January 2010.

[2] D.P. Shamonin, E.E. Bron, B.P.F. Lelieveldt, M. Smits, S. Klein and M. Staring, "Fast Parallel Image Registration on CPU and GPU for Diagnostic Classification of Alzheimer's Disease", Frontiers in Neuroinformatics, vol. 7, no. 50, pp. 1-15, January 2014.

[3] Kasper Marstal, Floris Berendsen, Marius Staring and Stefajkn Klein, "SimpleElastix: A user-friendly, multi-lingual library for medical image registration", International Workshop on Biomedical Image Registration (WBIR), Las Vegas, Nevada, USA, 2016.

[4] K. Ntatsis, N. Dekker, V. Valk, T. Birdsong, D. Zukić, S. Klein, M Staring, M McCormick, "itk-elastix: Medical image registration in Python", Proceedings of the 22nd Python in Science Conference, pp. 101 - 105, 2023, https://doi.org/10.25080/gerudo-f2bc6f59-00d.

[5] Rémi Flamary, Nicolas Courty, Alexandre Gramfort, Mokhtar Z. Alaya, Aurélie Boisbunon, Stanislas Chambon, Laetitia Chapel, Adrien Corenflos, Kilian Fatras, Nemo Fournier, Léo Gautheron, Nathalie T.H. Gayraud, Hicham Janati, Alain Rakotomamonjy, Ievgen Redko, Antoine Rolet, Antony Schutz, Vivien Seguy, Danica J. Sutherland, Romain Tavenard, Alexander Tong, Titouan Vayer, POT Python Optimal Transport library, Journal of Machine Learning Research, 22(78):1−8, 2021.

[6] Titouan Vayer, Laetitia Chapel, Rémi Flamary, Romain Tavenard, Nicolas Courty, Optimal Transport for structured data with application on graphs, Proceedings of the 36th International Conference on Machine Learning, pp.6275-6284, PMLR 97, 2019.



