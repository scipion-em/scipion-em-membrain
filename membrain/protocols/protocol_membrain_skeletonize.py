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
from typing import Union
from membrain import Plugin, OUTPUT_TOMOMASK_NAME
from pwem.convert.headers import setMRCSamplingRate
from pwem.protocols import EMProtocol
from pyworkflow import BETA
from pyworkflow.object import Pointer, Set
from pyworkflow.protocol import STEPS_PARALLEL, PointerParam, GPU_LIST, StringParam, LEVEL_ADVANCED
from pyworkflow.utils import Message, removeBaseExt
from tomo.objects import SetOfTomoMasks, TomoMask

# Inputs
IN_TOMO_MASKS = 'inTomoMasks'

# Suffixes
SUFFIX_SKEL = 'skel'


class ProtMemBrainSkeletonize(EMProtocol):
    """
    Generate a skeletonized version of the membrane segmentations, similar to the output of tomosegmemtv (
    https://github.com/anmartinezs/pyseg_system/tree/master/code/tomosegmemtv)

    More info:
        https://teamtomo.org/membrain-seg/Usage/Segmentation/
    """

    _label = 'tomomask skeletonize'
    _possibleOutputs = {OUTPUT_TOMOMASK_NAME: 'SetOfTomoMasks'}
    _devStatus = BETA
    stepsExecutionMode = STEPS_PARALLEL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tomoMaskDict = None

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam(IN_TOMO_MASKS, PointerParam,
                      pointerClass='SetOfTomoMasks',
                      allowsNull=False,
                      label='Input tomo masks (segmentations)')
        form.addHidden(GPU_LIST, StringParam,
                       default='0',
                       expertLevel=LEVEL_ADVANCED,
                       label='Choose GPU IDs',
                       help='GPU device to be used. If no GPU is found, MemBrain-seg will run on CPU using the number of threads specified (much slower)')

        form.addParallelSection(threads=1, mpi=0)

    # -------------------------- INSERT steps functions -----------------------
    def _insertAllSteps(self):
        deps = []
        self._initialize()
        for tomoId in self.tomoMaskDict.keys():
            mbId = self._insertFunctionStep(self._runMembrainSkel,
                                            tomoId,
                                            prerequisites=[],
                                            needsGPU=True)
            cOutId = self._insertFunctionStep(self._createOutputStep,
                                              tomoId,
                                              prerequisites=mbId,
                                              needsGPU=False)
            deps.append(cOutId)
        self._insertFunctionStep(self._closeOutputSet,
                                 prerequisites=deps,
                                 needsGPU=False)

    def _initialize(self):
        self.tomoMaskDict = {tomoMask.getTsId(): tomoMask.clone() for tomoMask in self._getInTomoMasks()}

    def _runMembrainSkel(self, tomoId: str):
        tomoMask = self.tomoMaskDict[tomoId]
        args = f'skeletonize --label-path {tomoMask.getFileName()} --out-folder {self._getExtraPath()}'
        self.runJob(Plugin.getMemBrainSegCmd(), args)

    def _createOutputStep(self, tomoId: str):
        inTomoMask = self.tomoMaskDict[tomoId]
        outFilename = self._getOutFileNameScipion(inTomoMask.getFileName())
        setMRCSamplingRate(outFilename, inTomoMask.getSamplingRate())
        outTomoSegs = self._createOutputSet()
        inTomoFileName = inTomoMask.getVolName()
        tomoMask = TomoMask()
        tomoMask.copyInfo(inTomoMask)
        tomoMask.setFileName(outFilename)
        tomoMask.setVolName(inTomoFileName)
        outTomoSegs.append(tomoMask)
        outTomoSegs.write()
        self._store(outTomoSegs)

    # --------------------------- UTILS functions ----------------------------------
    def _getInTomoMasks(self, retPointer: bool = False) -> Union[SetOfTomoMasks, Pointer]:
        inTomoMasksPointer = getattr(self, IN_TOMO_MASKS)
        return inTomoMasksPointer if retPointer else inTomoMasksPointer.get()

    def _createOutputSet(self) -> SetOfTomoMasks:
        outTomoMasks = getattr(self, OUTPUT_TOMOMASK_NAME, None)
        if outTomoMasks:
            outTomoMasks.enableAppend()
        else:
            outTomoMasks = SetOfTomoMasks.create(self._getPath(),
                                                template='tomomasks%s.sqlite',
                                                suffix=SUFFIX_SKEL)
            inTomoSet = self._getInTomoMasks()
            outTomoMasks.copyInfo(inTomoSet)
            outTomoMasks.setStreamState(Set.STREAM_OPEN)

            self._defineOutputs(**{OUTPUT_TOMOMASK_NAME: outTomoMasks})
            self._defineSourceRelation(self._getInTomoMasks(retPointer=True), outTomoMasks)

        return outTomoMasks

    def _getOutFileNameScipion(self, tomoMaskFName: str) -> str:
        return self._getExtraPath(f'{removeBaseExt(tomoMaskFName)}_{SUFFIX_SKEL}.mrc')

