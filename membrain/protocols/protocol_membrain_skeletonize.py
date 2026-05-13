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
    Generate a skeletonized version of the membrane segmentations, similar to the output of tomosegmemtv.
    (https://github.com/anmartinezs/pyseg_system/tree/master/code/tomosegmemtv)
    More info: https://teamtomo.org/membrain-seg/Usage/Segmentation/

    AI Generated:

    MemBrain Skeletonize (ProtMemBrainSkeletonize) — User Manual
        Overview

        The MemBrain Skeletonize protocol generates simplified skeleton
        representations from membrane segmentation volumes obtained in
        cryo-electron tomography workflows. Its purpose is to convert dense
        membrane masks into thinner structural traces that preserve the
        essential topology and connectivity of the segmented membranes while
        reducing geometric complexity.

        Skeletonization is particularly useful in structural cell biology
        because it enables downstream quantitative analyses of membrane
        organization, connectivity, curvature, and network architecture.
        Instead of working with full volumetric segmentations, researchers can
        analyze compact representations that highlight the central paths and
        structural continuity of membrane systems.

        This protocol is conceptually similar to the skeletonization procedures
        traditionally associated with tomosegmemtv workflows and is integrated
        into modern MemBrain-seg processing pipelines for tomographic membrane
        analysis.

        Inputs and Biological Context

        The protocol requires one or more membrane segmentation masks as input.
        These segmentations typically originate from automated or semi-automated
        membrane detection methods applied to cryo-electron tomography data.
        Each mask represents regions interpreted as biological membranes within
        the tomographic volume.

        In practical biological studies, these segmentations may correspond to
        organelle membranes, vesicles, endoplasmic reticulum networks, plasma
        membranes, mitochondrial structures, or other intracellular membrane
        systems. Skeletonization provides a cleaner geometric abstraction that
        facilitates interpretation of membrane organization at the systems level.

        General Workflow

        During execution, the protocol processes each segmentation independently
        and produces a skeletonized membrane representation preserving the
        original spatial correspondence and tomographic metadata. The resulting
        skeletons remain associated with their parent tomograms and can therefore
        be integrated directly into larger cryo-electron tomography workflows.

        The workflow is designed for batch execution and supports parallel
        processing of multiple tomograms. This is especially important in
        high-throughput cryo-ET studies where large collections of membrane
        segmentations must be analyzed consistently.

        GPU Acceleration and Computational Performance

        The protocol supports GPU acceleration when compatible hardware is
        available. GPU execution significantly improves performance for large
        tomographic datasets, particularly when membrane segmentations contain
        extensive volumetric information or highly connected membrane systems.

        If GPU resources are unavailable, the protocol can still operate on CPU
        resources, although execution may become substantially slower for large
        tomograms. In practical facility environments, GPU acceleration is
        generally recommended for efficient large-scale membrane analysis.

        Interpretation of Skeletonized Membranes

        The resulting skeletons provide a reduced geometric description of the
        membrane architecture while preserving the biologically meaningful
        connectivity of the original segmentation. These skeletons are often
        easier to visualize and quantify than dense volumetric masks.

        From a biological perspective, skeletonization is especially useful for
        studying membrane continuity, branching behavior, tubular organization,
        and large-scale structural connectivity inside cells. For example,
        reticulated membrane systems such as the endoplasmic reticulum or
        mitochondrial networks can be analyzed more effectively through their
        skeleton representations.

        However, users should remember that skeletonization simplifies membrane
        geometry and may omit fine volumetric details such as membrane thickness
        or subtle local variations. Consequently, the skeleton should be viewed
        as a topological representation rather than a complete physical model of
        the membrane surface.

        Outputs and Integration

        The protocol produces a new set of tomographic masks corresponding to
        the skeletonized membrane representations. These outputs preserve the
        spatial calibration and metadata of the original segmentation dataset,
        enabling direct compatibility with visualization tools and downstream
        quantitative analysis workflows.

        The generated skeletons can be combined with additional analyses such as
        membrane graph extraction, connectivity measurements, curvature studies,
        or structural tracing pipelines. They are also useful for simplified
        visualization in crowded tomographic environments.

        Practical Recommendations

        For best biological results, the input membrane segmentations should be
        reasonably clean and continuous before skeletonization. Noisy or highly
        fragmented segmentations may produce unstable or biologically ambiguous
        skeletons.

        In many cryo-ET workflows, it is advisable to visually inspect membrane
        segmentations prior to skeletonization and, if necessary, refine the
        segmentation quality to avoid disconnected or artifactual structures.
        High-quality segmentation typically leads to much more interpretable
        skeleton representations.

        Final Perspective

        The MemBrain Skeletonize protocol provides a practical way to transform
        membrane segmentations into simplified structural representations that
        preserve membrane topology while facilitating quantitative and visual
        analysis. For cryo-electron tomography researchers studying complex
        intracellular membrane systems, skeletonization offers an efficient and
        biologically meaningful bridge between volumetric segmentation and
        network-level structural interpretation.
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

