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
import os.path
from datetime import datetime as dt

import pwem
from scipion.install.funcs import VOID_TGZ

# # Environment variables are imported from here:
# from .constants import *

_logo = "icon.png"
_references = ['lamm_membrain_2022']
__version__ = "0.1.0"

MB_SEG_VERSION = 'git'

# Use this variable to activate an environment from the Scipion conda
MEMBRAIN_SEG_ENV_VAR = "MEMBRAIN_SEG_ENV"
DEFAULT_MEMBRAIN_SEG_ENV = "membrain-seg"
# Use this general activation variable when installed outside Scipion:
MEMBRAIN_SEG_ENV_ACTIVATION_VAR = "MEMBRAIN_SEG_ENV_ACTIVATION"

# models
MODEL_VERSION = '10'
MODEL_PKG_NAME = 'membrain-seg-models'
MEMBRAIN_SEG_MODEL_VAR = 'MEMBRAIN_SEG_MODEL'
MEMBRAIN_SEG_MODEL = 'MemBrain_seg_v10_alpha.ckpt'
GDRIVE_FILEID = '1tSQIz_UCsQZNfyHg0RxD-4meFgolszo8'


class Plugin(pwem.Plugin):

    _url = 'https://github.com/scipion-em/scipion-em-membrain'

    @classmethod
    def _defineVariables(cls):
        """ Defines variables for this plugin. scipion3 config -p membrain will show them with current values"""
        cls._defineVar(MEMBRAIN_SEG_ENV_VAR, DEFAULT_MEMBRAIN_SEG_ENV)
        # cls._defineVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR, cls.getMemBrainSegActivation())
        # cls._defineVar(MEMBRAIN_SEG_MODEL_VAR, MEMBRAIN_SEG_MODEL)

    @classmethod
    def getMemBrainSegActivation(cls):
        return "conda activate " + cls.getVar(MEMBRAIN_SEG_ENV_VAR)

    @classmethod
    def getMemBrainSegCmd(cls):
        """ Return the full command to run a MemBrain program. """
        cmd = cls.getVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR)
        if not cmd:
            cmd = cls.getCondaActivationCmd() + " "
            cmd += cls.getMemBrainSegActivation()
            cmd += " && membrain "
        return cmd

    @classmethod
    def getMemBrainSegModelPath(cls):
        """ Return the current MemBrain-seg model defined by the environment variable """
        model = cls.getVar(MEMBRAIN_SEG_MODEL_VAR)
        if not model:
            model = pwem.Config.EM_ROOT
            model += "/" + MODEL_PKG_NAME + "-" + MODEL_VERSION
            model += "/" + MEMBRAIN_SEG_MODEL
        return model

    @classmethod
    def defineBinaries(cls, env):

        def getCondaInstallation(version):

            installationCmd = cls.getCondaActivationCmd()
            installationCmd += ' conda create -y --name ' + \
                cls.getVar(MEMBRAIN_SEG_ENV_VAR) + ' python=3.9 && '
            installationCmd += cls.getMemBrainSegActivation() + ' && '
            installationCmd += 'cd membrain-seg && '
            installationCmd += 'pip install . && '
            installationCmd += 'touch ../env-created.txt'

            return installationCmd

        def defineMemBrainSegInstallation(version):
            installed = "last-pull-%s.txt" % dt.now().strftime("%y%h%d-%H%M%S")

            membrain_commands = [
                ('git clone https://github.com/teamtomo/membrain-seg.git', 'membrain-seg'),
                ('cd membrain-seg && git pull && touch ../%s' %
                 installed, installed),
                (getCondaInstallation(version), 'env-created.txt')
            ]

            env.addPackage('membrain-seg', version=version,
                           commands=membrain_commands,
                           tar=VOID_TGZ,
                           default=True)

        def getModelInstallation(model_version):

            # wget download line obtained from: https://stackoverflow.com/a/39087286
            modelInstallationCmd = 'curl -L -o ' + MEMBRAIN_SEG_MODEL + \
                ' "https://drive.google.com/uc?export=download&id=' + \
                GDRIVE_FILEID + '&confirm=yes" && '
            modelInstallationCmd += 'touch model-downloaded.txt'

            env.addPackage(MODEL_PKG_NAME, version=model_version,
                           commands=[
                               (modelInstallationCmd, 'model-downloaded.txt')],
                           tar=VOID_TGZ,
                           default=True)

        defineMemBrainSegInstallation(MB_SEG_VERSION)

        getModelInstallation(MODEL_VERSION)
