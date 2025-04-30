# **************************************************************************
# *
# * Authors:     Scipion Team
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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
from typing import Tuple

import pyworkflow.tests as pwtests
from membrain.protocols import ProtMemBrainSeg, ProtMemBrainSkeletonize
from membrain.protocols.protocol_membrain_seg import OUTPUT_TOMOMASK_NAME, OUTPUT_TOMOPROBMAP_NAME
from pyworkflow.utils import magentaStr, createLink
from tomo.objects import SetOfTomoMasks, SetOfTomograms
from tomo.protocols import ProtImportTomograms
from tomo.protocols.protocol_import_tomograms import OUTPUT_NAME
from tomo.tests import TOMOSEGMEMTV_TEST_DATASET, DataSet_Tomosegmemtv
from tomo.tests.test_base_centralized_layer import TestBaseCentralizedLayer


class TestMembrain(TestBaseCentralizedLayer):
    virtualTomo2 = None
    virtualTomo1 = None
    samplingRate = DataSet_Tomosegmemtv.sRate.value
    tomoDims = DataSet_Tomosegmemtv.tomoDims.value

    @classmethod
    def setUpClass(cls):
        pwtests.setupTestProject(cls)
        ds = pwtests.DataSet.getDataSet(TOMOSEGMEMTV_TEST_DATASET)
        cls.ds = ds
        # Because only one tomogram is provided in the tutorial, 2 links will be created pointing to the same file, so
        # they can be interpreted as a set of two tomograms, making the test complexity closer to the real usage
        cls.virtualTomos = ['vTomo1', 'vTomo2']
        virtualTomos = [cls.getOutputPath( fpath + '.mrc') for fpath in cls.virtualTomos]
        [createLink(ds.getFile(DataSet_Tomosegmemtv.tomogram.name), virtualTomo) for virtualTomo in virtualTomos]

    def _importTomograms(self) -> SetOfTomograms:
        print(magentaStr("\n==> Importing data - tomograms:"))
        protImportTomo = self.newProtocol(
            ProtImportTomograms,
            filesPath=self.getOutputPath(),
            filesPattern='vTomo*.mrc',
            samplingRate=self.samplingRate
        )
        protImportTomo = self.launchProtocol(protImportTomo)
        return getattr(protImportTomo, OUTPUT_NAME, None)

    def _runMembrainSeg(self, inTomograms: SetOfTomograms,
                        storeProbabilities: bool = False) -> Tuple[SetOfTomoMasks, SetOfTomoMasks]:
        print(magentaStr("\n==> Segmenting the membranes:"))
        protMembrainSeg = self.newProtocol(
            ProtMemBrainSeg,
            inTomograms=inTomograms,
            storeProbabilities=storeProbabilities)
        protMembrainSeg = self.launchProtocol(protMembrainSeg)
        return (getattr(protMembrainSeg, OUTPUT_TOMOMASK_NAME, None),
                getattr(protMembrainSeg, OUTPUT_TOMOPROBMAP_NAME, None))

    def _runMembrainSkel(self, inTomomasks: SetOfTomoMasks) -> SetOfTomoMasks:
        print(magentaStr("\n==> Skeletonizing the membranes:"))
        protMembrainSkel = self.newProtocol(ProtMemBrainSkeletonize,
                                            inTomoMasks=inTomomasks)
        protMembrainSkel = self.launchProtocol(protMembrainSkel)
        return getattr(protMembrainSkel, OUTPUT_TOMOMASK_NAME, None)


    def _checkTomoMasks(self, tomoMasks: SetOfTomoMasks):
        self.checkTomoMasks(tomoMasks,
                            expectedSetSize=2,
                            expectedSRate=self.samplingRate,
                            expectedDimensions=self.tomoDims,
                            isHeterogeneousSet=False)

    def test_membrain_seg_01(self):
        importedTomos = self._importTomograms()
        tomoMasks, tomoScores = self._runMembrainSeg(importedTomos)
        # Check the output sets
        self._checkTomoMasks(tomoMasks)
        self.assertIsNone(tomoScores)

    def test_membrain_seg_02(self):
        importedTomos = self._importTomograms()
        tomoMasks, tomoScores = self._runMembrainSeg(importedTomos,
                                                     storeProbabilities=True)
        # Check the output sets
        self._checkTomoMasks(tomoMasks)
        self._checkTomoMasks(tomoScores)

    def test_membrain_skel_01(self):
        importedTomos = self._importTomograms()
        tomoMasks, _ = self._runMembrainSeg(importedTomos)
        tomoMasksSkel = self._runMembrainSkel(tomoMasks)
        self._checkTomoMasks(tomoMasksSkel)



