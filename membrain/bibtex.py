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
	month = sep,
	year = {2022},
	keywords = {Cryo-electron tomography, deep learning, membrane protein, particle picking, annotation-efficient, protein localization},
	pages = {106990},
	file = {Lamm et al. - 2022 - MemBrain A deep learning-aided pipeline for detec.pdf:C\:\\Users\\diogori\\Zotero\\storage\\IW6YQWG4\\Lamm et al. - 2022 - MemBrain A deep learning-aided pipeline for detec.pdf:application/pdf},
}


"""
