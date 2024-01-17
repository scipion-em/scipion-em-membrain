# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Ricardo D. Righetto (ricardo.righetto@unibas.ch)
# *
# * University of Basel
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

"""

@article{lamm_membrain_2022,
	title = {{MemBrain}: {A} deep learning-aided pipeline for detection of membrane proteins in {Cryo}-electron tomograms},
	volume = {224},
	issn = {0169-2607},
	shorttitle = {{MemBrain}},
	url = {https://www.sciencedirect.com/science/article/pii/S0169260722003728},
	doi = {10.1016/j.cmpb.2022.106990},
	abstract = {Background and Objective
Cryo-electron tomography (cryo-ET) is an imaging technique that enables 3D visualization of the native cellular environment at sub-nanometer resolution, providing unpreceded insights into the molecular organization of cells. However, cryo-electron tomograms suffer from low signal-to-noise ratios and anisotropic resolution, which makes subsequent image analysis challenging. In particular, the efficient detection of membrane-embedded proteins is a problem still lacking satisfactory solutions.
Methods
We present MemBrain ? a new deep learning-aided pipeline that automatically detects membrane-bound protein complexes in cryo-electron tomograms. After subvolumes are sampled along a segmented membrane, each subvolume is assigned a score using a convolutional neural network (CNN), and protein positions are extracted by a clustering algorithm. Incorporating rotational subvolume normalization and using a tiny receptive field simplify the task of protein detection and thus facilitate the network training.
Results
MemBrain requires only a small quantity of training labels and achieves excellent performance with only a single annotated membrane (F1 score: 0.88). A detailed evaluation shows that our fully trained pipeline outperforms existing classical computer vision-based and CNN-based approaches by a large margin (F1 score: 0.92 vs. max. 0.63). Furthermore, in addition to protein center positions, MemBrain can determine protein orientations, which has not been implemented by any existing CNN-based method to date. We also show that a pre-trained MemBrain program generalizes to tomograms acquired using different cryo-ET methods and depicting different types of cells.
Conclusions
MemBrain is a powerful and annotation-efficient tool for the detection of membrane protein complexes in cryo-ET data, with the potential to be used in a wide range of biological studies. It is generalizable to various kinds of tomograms, making it possible to use pretrained models for different tasks. Its efficiency in terms of required annotations also allows rapid training and fine-tuning of models. The corresponding code, pretrained models, and instructions for operating the MemBrain program can be found at: https://github.com/CellArchLab/MemBrain.},
	language = {en},
	urldate = {2022-07-18},
	journal = {Computer Methods and Programs in Biomedicine},
	author = {Lamm, Lorenz and Righetto, Ricardo D. and Wietrzynski, Wojciech and Pöge, Matthias and Martinez-Sanchez, Antonio and Peng, Tingying and Engel, Benjamin D.},
	month = {sep},
	year = {2022},
	keywords = {Cryo-electron tomography, deep learning, membrane protein, particle picking, annotation-efficient, protein localization},
	pages = {106990},
	file = {Lamm et al. - 2022 - MemBrain A deep learning-aided pipeline for detec.pdf:C\:\\Users\\diogori\\Zotero\\storage\\IW6YQWG4\\Lamm et al. - 2022 - MemBrain A deep learning-aided pipeline for detec.pdf:application/pdf},
}

@misc{lamm_membrain_2024,
	title = {{MemBrain} v2: an end-to-end tool for the analysis of membranes in cryo-electron tomography},
	copyright = {© 2024, Posted by Cold Spring Harbor Laboratory. This pre-print is available under a Creative Commons License (Attribution 4.0 International), CC BY 4.0, as described at http://creativecommons.org/licenses/by/4.0/},
	shorttitle = {{MemBrain} v2},
	url = {https://www.biorxiv.org/content/10.1101/2024.01.05.574336v1},
	doi = {10.1101/2024.01.05.574336},
	abstract = {MemBrain v2 is a deep learning-enabled program aimed at the efficient analysis of membranes in cryo-electron tomography (cryo-ET). The final v2 release of MemBrain will comprise three main modules: 1) MemBrain-seg, which provides automated membrane segmentation, 2) MemBrain-pick, which provides automated picking of particles along segmented membranes, and 3) MemBrain-stats, which provides quantitative statistics of particle distributions and membrane morphometrics. This initial version of the manuscript is focused on the beta release of MemBrain-seg, which combines iterative training with diverse data and specialized Fourier-based data augmentations. These augmentations are specifically designed to enhance the tool's adaptability to a variety of tomographic data and address common challenges in cryo-ET analysis. A key feature of MemBrain-seg is the implementation of the Surface-Dice loss function, which improves the network's focus on membrane connectivity and allows for the effective incorporation of manual annotations from different sources. This function is beneficial in handling the variability inherent in membrane structures and annotations. Our ongoing collaboration with the cryo-ET community plays an important role in continually improving MemBrain v2 with a wide array of training data. This collaborative approach ensures that MemBrain v2 remains attuned to the field's needs, enhancing its robustness and generalizability across different types of tomographic data. The current version of MemBrain-seg is available at https://github.com/teamtomo/membrain-seg, and the predecessor of MemBrain-pick (also called MemBrain v1) is deposited at https://github.com/CellArchLab/MemBrain. This preprint will be updated concomitantly with the code until the three integrated modules of MemBrain v2 are complete.},
	language = {en},
	urldate = {2024-01-08},
	publisher = {bioRxiv},
	author = {Lamm, Lorenz and Zufferey, Simon and Righetto, Ricardo D. and Wietrzynski, Wojciech and Yamauchi, Kevin A. and Burt, Alister and Liu, Ye and Zhang, Hanyi and Martinez-Sanchez, Antonio and Ziegler, Sebastian and Isensee, Fabian and Schnabel, Julia A. and Engel, Benjamin D. and Peng, Tingying},
	month = jan,
	year = {2024},
	note = {Pages: 2024.01.05.574336
Section: New Results},
	keywords = {Favorites},
	file = {Full Text PDF:C\:\\Users\\diogori\\Zotero\\storage\\J9Y48BK5\\Lamm et al. - 2024 - MemBrain v2 an end-to-end tool for the analysis o.pdf:application/pdf},
}

"""
