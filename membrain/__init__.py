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

import pwem
from scipion.install.funcs import VOID_TGZ

# Environment variables are imported from here:
from .constants import *

_logo = "icon.png"
_references = ['lamm_membrain_2022']
__version__ = "0.1.0"

class Plugin(pwem.Plugin):
    
    @classmethod
    def _defineVariables(cls):
        """ Defines variables for this plugin. scipion3 config -p membrain will show them with current values"""
        cls._defineVar(MEMBRAIN_SEG_ENV_VAR, DEFAULT_MEMBRAIN_SEG_ENV)
        cls._defineVar(MEMBRAIN_SEG_ENV_ACTIVATION_VAR, cls.getMemBrainSegActivation())

    @classmethod
    def getMemBrainSegActivation(cls):
        return "conda activate " + cls.getVar(MEMBRAIN_SEG_ENV_VAR)

    @classmethod
    def getMemBrainCmd(cls):
        """ Return the full command to run a MemBrain program. """
        cmd = cls.getVar(MEMBRAIN_SEG_ACTIVATION_VAR)
        if not cmd:
            cmd = cls.getCondaActivationCmd()
            cmd += cls.getVargetMemBrainActivation()
        cmd += " && membrain"
        return cmd

    @classmethod
    def defineBinaries(cls, env):

        def defineMemBrainSegInstallation(version):
            installed = "last-pull-%s.txt" % dt.now().strftime("%y%h%d-%H%M%S")

            membrain_commands = [
                ('git clone https://github.com/teamtomo/membrain-seg.git', 'membrain-seg'),
                ('cd membrain-seg && git pull && touch ../%s' % installed, installed),
                (getCondaInstallation(version), 'env-created.txt')
            ]

            env.addPackage('membrain-seg', version=version,
                           commands=membrain_commands,
                           tar=VOID_TGZ,
                           default=True)

        def getCondaInstallation(version):
            installationCmd = cls.getCondaActivationCmd()
            installationCmd += 'conda create --name ' + DEFAULT_MEMBRAIN_SEG_ENV + ' python=3.9 && '
            installationCmd += cls.getMemBrainActivation() + ' && '
            installationCmd += 'cd membrain-seg && '
            installationCmd += 'pip install . && '
            installationCmd += 'touch ../env-created.txt'

        def getModelInstallation(model_version):

            # wget download line obtained from: https://stackoverflow.com/a/39087286
            modelInstallationCmd = 'curl -L -o ' + MEMBRAIN_SEG_MODEL + ' "https://drive.google.com/uc?export=download&id=' + FILEID + '&confirm=yes"'

            env.addPackage('membrain-seg_models', version=model_version, commands=modelInstallationCmd, tar=VOID_TGZ, default=True)