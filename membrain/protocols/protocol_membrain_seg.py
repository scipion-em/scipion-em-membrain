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
A protocol to segment membranes in tomograms using MemBrain-seg.
"""
from os.path import basename
from typing import Union

from membrain import Plugin, OUTPUT_TOMOMASK_NAME
from pwem.protocols import EMProtocol
from pyworkflow import BETA
from pyworkflow.object import Set, Pointer
from pyworkflow.protocol import PointerParam, BooleanParam, IntParam, FloatParam, StringParam, LEVEL_ADVANCED
from pyworkflow.utils import *
from tomo.objects import SetOfTomoMasks, TomoMask, SetOfTomograms
from pyworkflow.protocol.constants import STEPS_PARALLEL
from pyworkflow.protocol import GPU_LIST

# Inputs
IN_TOMOS = 'inTomograms'

# Suffixes
SUFFIX_SEG = 'segmented'
SUFFIX_SCORES = 'scores'

# Outputs
OUTPUT_TOMOPROBMAP_NAME = 'tomoProbMaps'


class ProtMemBrainSeg(EMProtocol):
    """
    Segment membranes in tomograms using MemBrain-seg.

    More info:
        https://github.com/teamtomo/membrain-seg
    """

    _label = 'tomogram membrane segmentation'
    _possibleOutputs = {OUTPUT_TOMOMASK_NAME: 'SetOfTomoMasks',
                        OUTPUT_TOMOPROBMAP_NAME: 'SetOfTomoMasks'}
    _devStatus = BETA
    stepsExecutionMode = STEPS_PARALLEL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tomoDict = None

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """

        # The most basic segmentation command is as follows:
        # membrain segment --ckpt-path $MEMBRAIN_SEG_MODEL --tomogram-path <path-to-your-tomo> --out-folder <your-preferred-folder>

        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam(IN_TOMOS, PointerParam,
                      pointerClass='SetOfTomograms',
                      allowsNull=False,
                      label='Input tomograms')

        form.addParam('segmentationThreshold', FloatParam,
                      default=0.0,
                      expertLevel=LEVEL_ADVANCED,
                      label='Threshold for segmentation',
                      help='Threshold for the membrane segmentation. Only voxels with a membrane score higher than this threshold will be segmented.')

        form.addParam('slidingWindowSize', IntParam,
                      default=160,
                      expertLevel=LEVEL_ADVANCED,
                      label='Sliding window size',
                      help='Sliding window size used for inference. Smaller values than 160 consume less GPU, but also lead to worse segmentation results!')

        form.addParam('additionalArgs', StringParam,
                      default="",
                      expertLevel=LEVEL_ADVANCED,
                      label='Additional options',
                      help='You can enter additional command line options to MemBrain here.')

        form.addSection(label='Connected components analysis')
        form.addParam('storeConnectedComponents', BooleanParam,
                      default=False,
                      label='Label connected components?',
                      help='Segmentation will be stored as labelled connected components (automatic annotation).')

        form.addParam('connectedComponentsThreshold', IntParam,
                      default=-1,
                      label='Threshold for connected components',
                      help='Components smaller than this size (in voxels) will be removed from the segmentation. A negative value disables this parameter.')

        form.addSection(label='Test-time augmentation (TTA)')
        form.addParam('testTimeAugmentation', BooleanParam,
                      default=True,
                      label='Do test-time augmentation?',
                      help='Use 8-fold test-time augmentation? This improves segmentation quality, but also increases runtime.')

        form.addParam('storeProbabilities', BooleanParam,
                      default=False,
                      label='Output probability maps?',
                      help='Stores probability maps obtained from 8-fold test-time augmentation in addition to the segmentations.')

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
        for tomoId in self.tomoDict.keys():
            mbId = self._insertFunctionStep(self.runMemBrainSeg,
                                            tomoId,
                                            prerequisites=[],
                                            needsGPU=True)
            cOutId = self._insertFunctionStep(self.createOutputStep,
                                              tomoId,
                                              prerequisites=mbId,
                                              needsGPU=False)
            deps.append(cOutId)
        self._insertFunctionStep(self._closeOutputSet,
                                 prerequisites=deps,
                                 needsGPU=False)


    def _initialize(self):
        self.tomoDict = {tomo.getTsId(): tomo.clone() for tomo in self._getInTomos()}

    def runMemBrainSeg(self, tomoId: str):
        tomo = self.tomoDict[tomoId]
        tomoFile = tomo.getFileName()

        # Arguments to the membrain command defined in the plugin initialization:
        args = ' segment '
        args += ' --ckpt-path ' + Plugin.getMemBrainSegModelPath()
        args += ' --tomogram-path ' + tomoFile
        args += ' --out-folder ' + self._getExtraPath()
        args += ' --segmentation-threshold ' + str(self.segmentationThreshold)
        args += ' --sliding-window-size ' + str(self.slidingWindowSize)

        if self.testTimeAugmentation:
            args += ' --test-time-augmentation'

            if self.storeProbabilities:
                args += ' --store-probabilities '

        else:
            args += ' --no-test-time-augmentation'

        if self.storeConnectedComponents:
            args += ' --store-connected-components '

            if self.connectedComponentsThreshold > 0:
                args += ' --connected-component-thres ' + \
                    str(self.connectedComponentsThreshold)
            
        args += " " + self.additionalArgs.get()

        self.runJob(Plugin.getMemBrainSegCmd(), args)

        outputFile = self._getOutFileNameMembrain(tomoFile)
        newOutputFile = self._getOutFileNameScipion(tomoId, SUFFIX_SEG)
        moveFile(outputFile, newOutputFile)

    # Output stuff is the same as in TomoSegMemTV protocol:
    def createOutputStep(self, tomoId: str):
        with self._lock:
            outTomoSegs = self._createOutputSet()
            inTomo = self.tomoDict[tomoId]
            inTomoFileName = inTomo.getFileName()
            tomoMask = TomoMask()
            tomoMask.copyInfo(inTomo)
            tomoMask.setFileName(self._getOutFileNameScipion(tomoId, SUFFIX_SEG))
            tomoMask.setVolName(inTomoFileName)
            outTomoSegs.append(tomoMask)
            outTomoSegs.write()
            self._store(outTomoSegs)

            if self.storeProbabilities:
                # We do the same thing again for the probability maps, if they exist:
                outTomoProbs = self._createOutputSet(isProbablityMap=True)
                tomoMask = TomoMask()
                tomoMask.copyInfo(inTomo)
                tomoMask.setFileName(self._getOutFileNameScipion(tomoId, SUFFIX_SCORES))
                tomoMask.setVolName(inTomoFileName)
                outTomoProbs.append(tomoMask)
                outTomoProbs.write()
                self._store(outTomoProbs)

    # --------------------------- UTILS functions ----------------------------------
    def _getInTomos(self, retPointer: bool = False) -> Union[SetOfTomograms, Pointer]:
        inTomosPointer = getattr(self, IN_TOMOS)
        return inTomosPointer if retPointer else inTomosPointer.get()

    def _createOutputSet(self, isProbablityMap: bool = False) -> SetOfTomoMasks:
        if isProbablityMap:
            outName = OUTPUT_TOMOPROBMAP_NAME
            suffix = SUFFIX_SCORES
        else:
            outName = OUTPUT_TOMOMASK_NAME
            suffix = SUFFIX_SEG
        outTomoMasks = getattr(self, outName, None)
        if outTomoMasks:
            outTomoMasks.enableAppend()
        else:
            outTomoMasks = SetOfTomoMasks.create(self._getPath(),
                                                template='tomomasks%s.sqlite',
                                                suffix=suffix)
            inTomoSet = self._getInTomos()
            outTomoMasks.copyInfo(inTomoSet)
            outTomoMasks.setStreamState(Set.STREAM_OPEN)

            self._defineOutputs(**{outName: outTomoMasks})
            self._defineSourceRelation(self._getInTomos(retPointer=True), outTomoMasks)

        return outTomoMasks

    def _getOutFileNameMembrain(self, tomoFileName: str) -> str:
        tomoBaseName = removeBaseExt(tomoFileName)
        modelBaseName = basename(Plugin.getMemBrainSegModelPath())
        return self._getExtraPath(f'{tomoBaseName}_{modelBaseName}_{SUFFIX_SEG}.mrc')

    def _getOutFileNameScipion(self, tomoId: str, suffix: str) -> str:
        return self._getExtraPath(f'{tomoId}_{suffix}.mrc')

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []

        if not self.testTimeAugmentation and self.storeProbabilities:
            errors.append(
                'Test-time augmentation must be enabled in order to store probability maps.')

        if self.connectedComponentsThreshold == 0:
            errors.append(
                'Connected components threshold threshold must be greater than zero, or negative to disable this option.')

        if self.slidingWindowSize.get() % 32 != 0:
            errors.append('Sliding window size must be multiple of 32.')
        return errors

    def _citations(self):

        cites = ['lamm_membrain_2024']

        return cites

    def _summary(self):
        summary = []
        nTomos = self.inTomograms.get().getSize()
        summary.append('%d tomograms segmented using MemBrain-seg.' % nTomos)

        summary.append(
            'A sliding window of size %d was used for prediction.' % self.slidingWindowSize)

        if self.testTimeAugmentation:
            summary.append(
                '8-fold test-time augmentation was used in each prediction.')
        else:
            summary.append(
                'Test-time augmentation was not used in prediction.')

        if self.storeProbabilities:
            summary.append(
                'Score maps based on test-time augmentation were saved in addition to segmentations.')

        if self.storeConnectedComponents:
            summary.append(
                'Segmentations were stored as labelled connected components.')

        if self.connectedComponentsThreshold > 0:
            summary.append('The threshold size for connected components was %d.' %
                           self.connectedComponentsThreshold)

        return summary
