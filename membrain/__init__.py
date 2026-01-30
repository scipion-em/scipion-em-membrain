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
from os.path import join, exists
import pwem
from pyworkflow import TOMO
from scipion.install.funcs import VOID_TGZ
from membrain.constants import *

_logo = "icon.png"
_references = ['lamm_membrain_2022', 'lamm_membrain_2024']
__version__ = "3.1.2"

class Plugin(pwem.Plugin):
    _url = 'https://github.com/scipion-em/scipion-em-membrain'
    _processingField = [TOMO]

    @classmethod
    def _defineVariables(cls):
        """ Defines variables for this plugin. scipion3 config -p membrain will show them with current values"""
        cls._defineVar(MEMBRAIN_SEG_ENV_VAR, MEMBRAIN_SEG_ENV_DEFAULT)
        cls._defineVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR, MEMBRAIN_SEG_ENV_ACTIVATION_DEFAULT)
        cls._defineEmVar(MEMBRAIN_SEG_HOME, MEMBRAIN_SEG + '-' + MEMBRAIN_SEG_VERSION)
        cls._defineEmVar(MODEL_MODELS_HOME, MEMBRAIN_SEG_MODELS_DIR)
        cls._defineVar(MEMBRAIN_SEG_MODEL_VAR, MEMBRAIN_SEG_MODEL_NAME_DEFAULT)

    @classmethod
    def getMemBrainSegActivation(cls):
        return cls.getVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR)

    @classmethod
    def getMemBrainSegCmd(cls):
        """ Return the full command to run a MemBrain program. """
        cmd = cls.getCondaActivationCmd() + " "
        cmd += cls.getMemBrainSegActivation()
        cmd += " && CUDA_VISIBLE_DEVICES=%(GPU)s membrain "
        return cmd

    @classmethod
    def getMemBrainSegModelPath(cls):
        """ Return the current MemBrain-seg model defined by the environment variable """
        return join(cls.getVar(MODEL_MODELS_HOME), cls.getVar(MEMBRAIN_SEG_MODEL_VAR))

    @classmethod
    def defineBinaries(cls, env):
        ENV_CREATED = 'env-created'
        MEMBRAIN_SEG_INSTALLED = '%s_%s_installed' % (MEMBRAIN_SEG, MEMBRAIN_SEG_VERSION)
        MODEL_DOWNLOADED = 'model-downloaded'

        # Conda env
        envInstCmd = cls.getCondaActivationCmd()
        envInstCmd += ' conda create -y --name ' + \
                           cls.getVar(MEMBRAIN_SEG_ENV_VAR) + ' -c conda-forge python=3.9 && '
        envInstCmd += f'touch {ENV_CREATED}'

        # Membrain-seg
        MembInstCmd = cls.getCondaActivationCmd() + " "
        MembInstCmd += cls.getMemBrainSegActivation() + ' && '
        MembInstCmd += 'pip install gdown && '  # We install gdown just to have a more stable way of downloading from Google Drive
        MembInstCmd += 'pip install %s==%s && ' % (MEMBRAIN_SEG, MEMBRAIN_SEG_VERSION)
        MembInstCmd += 'touch %s' % MEMBRAIN_SEG_INSTALLED

        # Download the model
        modelsHomeDir = cls.getVar(MODEL_MODELS_HOME)
        modelFilePath = join(modelsHomeDir, MEMBRAIN_SEG_MODEL_NAME_DEFAULT)
        modelInstallationCmd = cls.getCondaActivationCmd() + " "
        modelInstallationCmd += f'{cls.getMemBrainSegActivation()} '
        if not exists(modelsHomeDir):
            modelInstallationCmd += f'&& mkdir {modelsHomeDir} '
        if exists(modelsHomeDir) and not exists(modelFilePath):
            modelInstallationCmd += f'&& gdown {GDRIVE_FILEID} -O {MEMBRAIN_SEG_MODEL_NAME_DEFAULT} '
            modelInstallationCmd += f'&& mv {MEMBRAIN_SEG_MODEL_NAME_DEFAULT} {modelsHomeDir} '
        modelInstallationCmd += f'&& touch {MODEL_DOWNLOADED}'

        membrain_commands = [
            (envInstCmd, ENV_CREATED),
            (MembInstCmd, MEMBRAIN_SEG_INSTALLED),
            (modelInstallationCmd, MODEL_DOWNLOADED)
        ]

        env.addPackage(MEMBRAIN_SEG,
                       version=MEMBRAIN_SEG_VERSION,
                       commands=membrain_commands,
                       tar=VOID_TGZ,
                       default=True)

