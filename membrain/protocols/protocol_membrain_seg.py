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
    Segments cellular membranes in cryo-electron tomography datasets using
deep learning methods provided by MemBrain-seg. The protocol is designed to
identify membrane regions within tomograms and generate volumetric masks that
can be used for downstream structural interpretation, particle picking,
membrane analysis, or visualization workflows. It supports both standard
segmentation outputs and probability maps representing membrane confidence
scores derived from inference.
More info: https://github.com/teamtomo/membrain-seg

    AI Generated:

    MemBrain Membrane Segmentation (ProtMemBrainSeg) - User Manual
        Overview

        The MemBrain membrane segmentation protocol provides automated membrane
        detection for cryo-electron tomography data using neural-network-based
        inference methods. Its primary objective is to identify membrane-like
        structures inside tomograms and convert them into segmentation masks that
        can be further analyzed in biological studies. In tomographic workflows,
        membrane segmentation is often an essential preprocessing step for the
        study of organelles, vesicles, viral envelopes, intracellular membranes,
        and membrane-associated macromolecular complexes.

        For biological users, the protocol is particularly useful when handling
        large tomographic datasets where manual annotation would be impractical or
        excessively time consuming. Automated membrane segmentation allows rapid
        extraction of membrane geometries and facilitates downstream analyses such
        as curvature estimation, membrane tracing, subtomogram averaging
        preparation, or visualization of cellular organization.

        Inputs and General Workflow

        The protocol requires one or more tomograms as input. Each tomogram is
        independently processed to produce membrane segmentation masks. The
        workflow applies a pretrained MemBrain-seg model that evaluates local
        image information and predicts membrane probabilities across the entire
        tomographic volume.

        Segmentation results are stored as volumetric masks aligned with the
        original tomograms, preserving the geometric relationship between the
        segmented membranes and the biological sample. Optionally, probability
        maps can also be generated, allowing users to inspect the confidence of
        the predictions and adjust downstream interpretation accordingly.

        Segmentation Thresholds and Biological Interpretation

        One of the most important biological parameters is the segmentation
        threshold. This value determines which voxels are considered membrane
        regions based on their predicted membrane confidence score. Lower
        thresholds generally produce larger and more inclusive membrane regions,
        which may help recover weak or noisy membranes but can also introduce
        false positives. Higher thresholds produce cleaner and more conservative
        segmentations, although biologically relevant faint membranes may be
        missed.

        In practice, exploratory analyses often begin with intermediate threshold
        values followed by visual inspection. Biological samples with low signal,
        strong ice contamination, or highly curved membranes may require more
        permissive thresholds. Conversely, cleaner datasets with strong membrane
        contrast may benefit from stricter segmentation settings.

        Sliding Window Inference

        The protocol processes tomograms using a sliding window strategy. This
        approach allows large tomographic datasets to be segmented even when GPU
        memory resources are limited. The window size directly affects both
        segmentation quality and computational cost.

        Larger window sizes generally provide more contextual information to the
        neural network and often improve segmentation continuity and membrane
        recognition. However, they require more GPU memory and longer processing
        times. Smaller windows reduce computational demands but may introduce
        discontinuities or reduce segmentation quality in difficult regions.

        From a biological perspective, large membrane systems such as extended
        endoplasmic reticulum networks, mitochondrial cristae, or stacked
        membrane assemblies may particularly benefit from larger contextual
        windows.

        Test-Time Augmentation

        The protocol optionally supports test-time augmentation, an inference
        strategy that evaluates multiple transformed versions of the same data
        and combines the predictions into a consensus result. This usually
        improves segmentation robustness and reduces sensitivity to noise or
        directional artifacts.

        Biologically, test-time augmentation is especially valuable for noisy
        tomograms, low-dose acquisitions, or samples containing membranes with
        variable orientations and curvatures. Although this approach increases
        runtime, it often yields smoother and more reliable membrane detection.

        When enabled, the protocol can additionally generate probability maps.
        These maps are useful for advanced users who wish to evaluate prediction
        confidence or apply custom thresholding strategies in downstream analyses.

        Connected Components Analysis

        The protocol can optionally label segmented regions as connected
        components. This operation separates disconnected membrane structures and
        stores them as independently labeled objects. Such labeling can simplify
        the identification of isolated vesicles, organelles, or membrane patches
        within crowded cellular environments.

        A minimum size threshold may also be applied to remove very small
        connected regions. This is particularly useful for eliminating isolated
        noise artifacts or fragmented predictions that are unlikely to represent
        biologically meaningful membranes.

        From a biological perspective, careful selection of the connected
        component threshold is important. Excessively aggressive filtering may
        remove small but relevant membrane structures, while insufficient
        filtering may preserve noisy artifacts.

        Outputs and Their Interpretation

        The protocol produces segmented membrane masks for each input tomogram.
        These outputs retain the spatial dimensions and sampling information of
        the original datasets, enabling direct integration with visualization and
        analysis software commonly used in cryo-electron tomography workflows.

        When probability map generation is enabled, additional volumetric outputs
        containing membrane confidence values are also produced. These maps are
        particularly useful for quality assessment, threshold optimization, and
        quantitative analyses based on prediction confidence.

        The resulting segmentations can be used in many downstream biological
        applications, including membrane tracing, subtomogram particle selection,
        organelle morphology studies, structural annotation, and spatial analysis
        of membrane-associated complexes.

        Practical Recommendations

        For most biological applications, enabling test-time augmentation is
        recommended because it generally improves segmentation quality and
        robustness. Although runtime increases, the gain in segmentation
        consistency is often substantial, especially for noisy tomograms.

        Users working with limited GPU memory may reduce the sliding window size,
        but segmentation quality should always be visually inspected afterward.
        Larger windows are preferable whenever computational resources allow.

        Connected component labeling is particularly useful for cellular datasets
        containing many independent membrane structures. However, thresholding
        parameters should be selected carefully to avoid removing biologically
        meaningful small objects.

        Probability maps are valuable when segmentation confidence needs to be
        evaluated quantitatively or when additional downstream filtering is
        planned. For rapid exploratory analyses, standard segmentation masks are
        often sufficient.

        Final Perspective

        Automated membrane segmentation has become an essential capability in
        cryo-electron tomography because modern datasets are increasingly large
        and structurally complex. By combining deep learning segmentation with
        scalable tomographic processing, this protocol enables efficient and
        biologically meaningful extraction of membrane structures from cellular
        environments.

        Successful membrane analysis depends not only on computational accuracy
        but also on careful biological interpretation of segmentation thresholds,
        confidence maps, and connected structures. Thoughtful parameter selection
        and visual validation remain essential for obtaining reliable membrane
        representations suitable for downstream structural biology studies.
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
