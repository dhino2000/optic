# References

OPTIC builds on the following open-source libraries — please also cite the relevant work when you use OPTIC.

## Core dependencies

### Suite2p
- Repository: <https://github.com/MouseLand/suite2p>
- Pachitariu, M., Stringer, C., Schröder, S., Dipoppa, M., Rossi, L.F., Carandini, M., & Harris, K.D. (2016). *Suite2p: beyond 10,000 neurons with standard two-photon microscopy.* bioRxiv 061507v2. <https://doi.org/10.1101/061507>
- Stringer, C., Ki, C., DelGrosso, N., LaFosse, P., Zhang, Q., & Pachitariu, M. (2026). *Extracting large-scale neural activity with Suite2p.* bioRxiv 2026.02.04.703741v1. <https://doi.org/10.64898/2026.02.04.703741>

### CaImAn
- Repository: <https://github.com/flatironinstitute/CaImAn>
- Giovannucci, A., Friedrich, J., Gunn, P., Kalfon, J., Brown, B.L., Koay, S.A., Taxidis, J., Najafi, F., Gauthier, J.L., Zhou, P., Khakh, B.S., Tank, D.W., Chklovskii, D.B., & Pnevmatikakis, E.A. (2019). *CaImAn an open source tool for scalable calcium imaging data analysis.* eLife 8, e38173. <https://doi.org/10.7554/eLife.38173>

### Cellpose
- Repository: <https://github.com/MouseLand/cellpose>
- Stringer, C., Wang, T., Michaelos, M., & Pachitariu, M. (2021). *Cellpose: a generalist algorithm for cellular segmentation.* Nature Methods 18(1), 100–106. <https://doi.org/10.1038/s41592-020-01018-x>
- Pachitariu, M., & Stringer, C. (2022). *Cellpose 2.0: how to train your own model.* Nature Methods 19(12), 1634–1641. <https://doi.org/10.1038/s41592-022-01663-4>
- Stringer, C., & Pachitariu, M. (2025). *Cellpose3: one-click image restoration for improved cellular segmentation.* Nature Methods 22(3), 592–599. <https://doi.org/10.1038/s41592-025-02595-5>

### ITKElastix
- Repository: <https://github.com/InsightSoftwareConsortium/ITKElastix>
- Klein, S., Staring, M., Murphy, K., Viergever, M.A., & Pluim, J.P.W. (2010). *elastix: a toolbox for intensity based medical image registration.* IEEE Transactions on Medical Imaging 29(1), 196–205. <https://doi.org/10.1109/TMI.2009.2035616>
- Shamonin, D.P., Bron, E.E., Lelieveldt, B.P.F., Smits, M., Klein, S., & Staring, M. (2014). *Fast Parallel Image Registration on CPU and GPU for Diagnostic Classification of Alzheimer's Disease.* Frontiers in Neuroinformatics 7(50), 1–15. <https://doi.org/10.3389/fninf.2013.00050>
- Marstal, K., Berendsen, F., Staring, M., & Klein, S. (2016). *SimpleElastix: A user-friendly, multi-lingual library for medical image registration.* In: IEEE Conference on Computer Vision and Pattern Recognition Workshops (CVPRW), pp. 134–142. <https://doi.org/10.1109/CVPRW.2016.78>
- Ntatsis, K., Lowekamp, B., & Klein, S. (2023). *itk-elastix: Medical image registration in Python.* In: Proceedings of the 22nd Python in Science Conference (SciPy 2023), pp. 101–105. <https://proceedings.scipy.org/articles/gerudo-f2bc6f59-00d>

### POT (Python Optimal Transport)
- Repository: <https://github.com/PythonOT/POT>
- Flamary, R., Courty, N., Gramfort, A., Alaya, M.Z., Boisbunon, A., Chambon, S., Chapel, L., Corenflos, A., Fatras, K., Fournier, N., Gautheron, L., Gayraud, N.T.H., Janati, H., Rakotomamonjy, A., Redko, I., Rolet, A., Schutz, A., Seguy, V., Sutherland, D.J., Tavenard, R., Tong, A., & Vayer, T. (2021). *POT: Python Optimal Transport.* Journal of Machine Learning Research 22(78), 1–8. <http://jmlr.org/papers/v22/20-451.html>

### NetworkX
- Repository: <https://github.com/networkx/networkx>
- Hagberg, A.A., Schult, D.A., & Swart, P.J. (2008). *Exploring network structure, dynamics, and function using NetworkX.* In: Proceedings of the 7th Python in Science Conference (SciPy2008), pp. 11–15. <https://doi.org/10.25080/TCWV9851>

## BibTeX

```bibtex
@article {Stringer2026.02.04.703741,
	author = {Stringer, Carsen and Ki, Chris and DelGrosso, Nicholas and LaFosse, Paul and Zhang, Qingqing and Pachitariu, Marius},
	title = {Extracting large-scale neural activity with Suite2p},
	elocation-id = {2026.02.04.703741},
	year = {2026},
	doi = {10.64898/2026.02.04.703741},
	publisher = {Cold Spring Harbor Laboratory},
	abstract = {Neural recordings using optical methods have improved dramatically. For example, we demonstrate here recordings of over 100,000 neurons from the mouse cortex obtained with a standard commercial microscope. To process such large datasets, we developed Suite2p, a collection of efficient algorithms for motion correction, cell detection, activity extraction and quality control. We also developed new approaches to benchmark performance on these tasks. Our GPU-accelerated non-rigid motion correction substantially outperforms alternative methods, while running over five times faster. For cell detection, Suite2p outperforms the CNMF algorithm in Caiman and Fiola, finding more cells and producing fewer false positives, while running in a fraction of the time. We also introduce quality control steps for users to evaluate performance on their own data, while offering alternative algorithms for specialized types of recordings such as those from one-photon and voltage imaging.Competing Interest StatementThe authors have declared no competing interest.Howard Hughes Medical Institute, https://ror.org/006w34k90},
	URL = {https://www.biorxiv.org/content/early/2026/02/06/2026.02.04.703741},
	eprint = {https://www.biorxiv.org/content/early/2026/02/06/2026.02.04.703741.full.pdf},
	journal = {bioRxiv}
}

@article {10.7554/eLife.38173,
article_type = {journal},
title = {CaImAn an open source tool for scalable calcium imaging data analysis},
author = {Giovannucci, Andrea and Friedrich, Johannes and Gunn, Pat and Kalfon, Jérémie and Brown, Brandon L and Koay, Sue Ann and Taxidis, Jiannis and Najafi, Farzaneh and Gauthier, Jeffrey L and Zhou, Pengcheng and Khakh, Baljit S and Tank, David W and Chklovskii, Dmitri B and Pnevmatikakis, Eftychios A},
editor = {Kleinfeld, David and King, Andrew J},
volume = 8,
year = 2019,
month = {jan},
pub_date = {2019-01-17},
pages = {e38173},
citation = {eLife 2019;8:e38173},
doi = {10.7554/eLife.38173},
url = {https://doi.org/10.7554/eLife.38173},
abstract = {Advances in fluorescence microscopy enable monitoring larger brain areas in-vivo with finer time resolution. The resulting data rates require reproducible analysis pipelines that are reliable, fully automated, and scalable to datasets generated over the course of months. We present C\textsc{a}I\textsc{m}A\textsc{n}, an open-source library for calcium imaging data analysis. C\textsc{a}I\textsc{m}A\textsc{n} provides automatic and scalable methods to address problems common to pre-processing, including motion correction, neural activity identification, and registration across different sessions of data collection. It does this while requiring minimal user intervention, with good scalability on computers ranging from laptops to high-performance computing clusters. C\textsc{a}I\textsc{m}A\textsc{n} is suitable for two-photon and one-photon imaging, and also enables real-time analysis on streaming data. To benchmark the performance of C\textsc{a}I\textsc{m}A\textsc{n} we collected and combined a corpus of manual annotations from multiple labelers on nine mouse two-photon datasets. We demonstrate that C\textsc{a}I\textsc{m}A\textsc{n} achieves near-human performance in detecting locations of active neurons.},
keywords = {calcium imaging, open source, software, two-photon, one-photon, data analysis},
journal = {eLife},
issn = {2050-084X},
publisher = {eLife Sciences Publications, Ltd},
}

@article{Stringer2025,
  author    = {Stringer, Carsen and Pachitariu, Marius},
  title     = {Cellpose3: one-click image restoration for improved cellular segmentation},
  journal   = {Nature Methods},
  year      = {2025},
  month     = mar,
  day       = {1},
  volume    = {22},
  number    = {3},
  pages     = {592--599},
  issn      = {1548-7105},
  doi       = {10.1038/s41592-025-02595-5},
  url       = {https://doi.org/10.1038/s41592-025-02595-5},
}

@article{JMLR:v22:20-451,
  title   = {POT: Python Optimal Transport},
  author  = {R{\'e}mi Flamary and Nicolas Courty and Alexandre Gramfort and Mokhtar Z. Alaya and Aur{\'e}lie Boisbunon and Stanislas Chambon and Laetitia Chapel and Adrien Corenflos and Kilian Fatras and Nemo Fournier and L{\'e}o Gautheron and Nathalie T.H. Gayraud and Hicham Janati and Alain Rakotomamonjy and Ievgen Redko and Antoine Rolet and Antony Schutz and Vivien Seguy and Danica J. Sutherland and Romain Tavenard and Alexander Tong and Titouan Vayer},
  journal = {Journal of Machine Learning Research},
  year    = {2021},
  volume  = {22},
  number  = {78},
  pages   = {1-8},
  url     = {http://jmlr.org/papers/v22/20-451.html}
}

@article{hagberg2008,
  author = {Hagberg, Aric A. and Schult, Daniel A. and Swart, Pieter J.},
  title = {Exploring Network Structure, Dynamics, and Function using NetworkX},
  journal = {Python in Science Conference},
  year = {2008},
  doi = {10.25080/TCWV9851},
  url = {https://doi.org/10.25080/TCWV9851}
}
```
