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


'''
A protocol to segment membranes in tomograms using MemBrain-seg.
'''
import os
from enum import Enum
from membrain import Plugin
from membrain import utils as mbUtils
from pwem.protocols import EMProtocol
from pyworkflow import BETA
from pyworkflow.protocol import PointerParam, BooleanParam, IntParam, FloatParam, StringParam, LEVEL_ADVANCED
from pyworkflow.utils import *
from tomo.objects import SetOfTomoMasks, TomoMask
from pyworkflow.protocol.constants import STEPS_PARALLEL
from pyworkflow.protocol import GPU_LIST


OUTPUT_TOMOMASK_NAME = 'tomoMasks'
OUTPUT_TOMOPROBMAP_NAME = 'tomoProbMaps'
OUTPUT_DIR = 'extra/'


class ProtMemBrainSeg(EMProtocol):
    '''
    Segment membranes in tomograms using MemBrain-seg.

    More info:
        https://github.com/teamtomo/membrain-seg
    '''

    _label = 'tomogram membrane segmentation'
    _possibleOutputs = {OUTPUT_TOMOMASK_NAME: SetOfTomoMasks,
                        OUTPUT_TOMOPROBMAP_NAME: SetOfTomoMasks}
    _devStatus = BETA

    tomoMaskList = []
    tomoProbMapList = []

    def __init__(self, **args):
        EMProtocol.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        ''' Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        '''

        # The most basic segmentation command is as follows:
        # membrain segment --ckpt-path $MEMBRAIN_SEG_MODEL --tomogram-path <path-to-your-tomo> --out-folder <your-preferred-folder>

        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inTomograms', PointerParam,
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

        form.addHidden(GPU_LIST, StringParam, default='0',
                       expertLevel=LEVEL_ADVANCED,
                       label='Choose GPU IDs',
                       help='GPU device to be used. If no GPU is found, MemBrain-seg will run on CPU using the number of threads specified (much slower)')

        form.addParallelSection(threads=1, mpi=0)

    # -------------------------- INSERT steps functions -----------------------
    def _insertAllSteps(self):

        # Scipion's built-in GPU per-thread assignment seems broken so we need to do this:
        gpus = mbUtils.getGoodGpuList(self.gpuList.get())
        n_gpus = len(gpus)

        deps = []
        for i, tomo in enumerate(self.inTomograms.get()):
            gpu_idx = i % n_gpus
            deps.append(self._insertFunctionStep(self.runMemBrainSeg,
                        tomo.getFileName(), gpus[gpu_idx], prerequisites=[]))

        self._insertFunctionStep(self.createOutputStep, prerequisites=deps)

    def runMemBrainSeg(self, tomoFile: str, gpuID: str):

        gpuAssignment = "CUDA_VISIBLE_DEVICES=" + gpuID + "; "

        tomoBaseName = removeBaseExt(tomoFile)

        # Arguments to the membrain command defined in the plugin initialization:
        args = ' segment '
        args += ' --ckpt-path ' + Plugin.getMemBrainSegModelPath()
        args += ' --tomogram-path ' + tomoFile
        args += ' --out-folder ' + self.getWorkingDir() + '/' + OUTPUT_DIR + '/'
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

        self.runJob(gpuAssignment + Plugin.getMemBrainSegCmd(), args)

        modelBaseName = os.path.basename(Plugin.getMemBrainSegModelPath())
        OutputFile = self.getWorkingDir() + '/' + OUTPUT_DIR + '/' + tomoBaseName + \
            '_' + modelBaseName + '_segmented.mrc'
        NewOutputFile = self.getWorkingDir() + '/' + OUTPUT_DIR + '/' + \
            tomoBaseName + '_segmented.mrc'
        moveFile(OutputFile, NewOutputFile)

        self.tomoMaskList.append(NewOutputFile)

        if self.storeProbabilities:
            OutputProbFile = self.getWorkingDir() + '/' + OUTPUT_DIR + '/' + \
                tomoBaseName + '_scores.mrc'
            self.tomoProbMapList.append(OutputProbFile)

    # Output stuff is the same as in TomoSegMemTV protocol:
    def createOutputStep(self):
        labelledSet = self._genOutputSetOfTomoMasks(
            self.tomoMaskList, 'segmented')
        self._defineOutputs(**{OUTPUT_TOMOMASK_NAME: labelledSet})
        self._defineSourceRelation(self.inTomograms.get(), labelledSet)

        if self.tomoProbMapList:
            # We do the same thing again for the probability maps, if they exist:
            labelledSet = self._genOutputSetOfTomoMasks(
                self.tomoProbMapList, 'probability map')
            self._defineOutputs(**{OUTPUT_TOMOPROBMAP_NAME: labelledSet})
            self._defineSourceRelation(self.inTomograms.get(), labelledSet)

    def _genOutputSetOfTomoMasks(self, tomoMaskList, suffix):
        tomoMaskSet = SetOfTomoMasks.create(
            self._getPath(), template='tomomasks%s.sqlite', suffix=suffix)
        inTomoSet = self.inTomograms.get()
        tomoMaskSet.copyInfo(inTomoSet)
        counter = 1
        for file, inTomo in zip(tomoMaskList, inTomoSet):
            tomoMask = TomoMask()
            fn = inTomo.getFileName()
            tomoMask.copyInfo(inTomo)
            tomoMask.setLocation((counter, file))
            tomoMask.setVolName(self._getExtraPath(replaceBaseExt(fn, 'mrc')))
            tomoMaskSet.append(tomoMask)
            counter += 1

        return tomoMaskSet

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []

        if not self.testTimeAugmentation and self.storeProbabilities:
            errors.append(
                'Test-time augmentation must be enabled in order to store probability maps.')

        if self.connectedComponentsThreshold == 0:
            errors.append(
                'Connected components threshold threshold must be greater than zero, or negative to disable this option.')

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
