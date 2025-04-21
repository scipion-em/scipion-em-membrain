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
from scipion.install.funcs import VOID_TGZ
from membrain.constants import *

_logo = "icon.png"
_references = ['lamm_membrain_2022', 'lamm_membrain_2024']
__version__ = "3.0.0"

class Plugin(pwem.Plugin):

    _url = 'https://github.com/scipion-em/scipion-em-membrain'

    @classmethod
    def _defineVariables(cls):
        """ Defines variables for this plugin. scipion3 config -p membrain will show them with current values"""
        cls._defineVar(MEMBRAIN_SEG_ENV_VAR, DEFAULT_MEMBRAIN_SEG_ENV)
        cls._defineVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR, DEFAULT_MEMBRAIN_SEG_ENV_ACTIVATION)
        cls._defineVar(MEMBRAIN_SEG_MODEL_VAR, DEFAULT_MEMBRAIN_SEG_MODEL)

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
        # model = cls.getVar(MEMBRAIN_SEG_MODEL_VAR)
        # if not model:
        #     model = pwem.Config.EM_ROOT
        #     model += "/" + MODEL_PKG_NAME + "-" + MODEL_VERSION
        #     model += "/" + MEMBRAIN_SEG_MODEL
        # return model
        return cls.getVar(MEMBRAIN_SEG_MODEL_VAR)

    @classmethod
    def defineBinaries(cls, env):

        # Install basic conda environment with dependencies:
        def getCondaInstallation(version):

            installationCmd = cls.getCondaActivationCmd()
            installationCmd += ' conda create -y --name ' + \
                cls.getVar(MEMBRAIN_SEG_ENV_VAR) + ' -c conda-forge python=3.9 && '
            # installationCmd += cls.getMemBrainSegActivation() + ' && '
            installationCmd += 'touch env-created'

            return installationCmd

        # Install MemBrain-seg itself:
        def defineMemBrainSegInstallation(version):

            MEMBRAIN_SEG_INSTALLED = '%s_%s_installed' % (MEMBRAIN_SEG, MEMBRAIN_SEG_VERSION)

            installationCmd = cls.getCondaActivationCmd() + " "
            installationCmd += cls.getMemBrainSegActivation() + ' && '

            # Install a dependency for the scipion-em-membrain plugin:  
            # NOTE: this will change once we are able to fetch the model from Zenodo (coming soon)          
            installationCmd += 'pip install gdown && ' # We install gdown just to have a more stable way of downloading from Google Drive

            # Install MemBrain-Seg itself:
            installationCmd += 'pip install %s==%s && ' % (MEMBRAIN_SEG, MEMBRAIN_SEG_VERSION)

            # Flag installation finished
            installationCmd += 'touch %s' % MEMBRAIN_SEG_INSTALLED

            membrain_commands = [
                (getCondaInstallation(version), 'env-created'),
                (installationCmd, MEMBRAIN_SEG_INSTALLED)
            ]

            env.addPackage('membrain_seg', version=version,
                           commands=membrain_commands,
                           tar=VOID_TGZ,
                           default=True)

        def getModelInstallation(model_version):

            ## THIS DOES NOT WORK AS OF 16.01.2024:
            # wget download line obtained from: https://stackoverflow.com/a/39087286
            # modelInstallationCmd = 'curl -L -o ' + MEMBRAIN_SEG_MODEL + \
            #     ' "https://drive.google.com/uc?export=download&id=' + \
            #     GDRIVE_FILEID + '&confirm=yes" && '

            ## So we have to go with this:
            modelInstallationCmd = cls.getCondaActivationCmd() + " "
            modelInstallationCmd += cls.getMemBrainSegActivation()
            modelInstallationCmd += ' && gdown -O ' + MEMBRAIN_SEG_MODEL + ' ' + GDRIVE_FILEID
            modelInstallationCmd += ' && touch model-downloaded.txt'

            env.addPackage(MODEL_PKG_NAME, version=model_version,
                           commands=[
                               (modelInstallationCmd, 'model-downloaded.txt')],
                           tar=VOID_TGZ,
                           default=True)

        defineMemBrainSegInstallation(MEMBRAIN_SEG_VERSION)

        getModelInstallation(MODEL_VERSION)
