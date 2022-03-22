# **************************************************************************
# *
# * Authors:     you (you@yourinstitution.email)
# *
# * your institution
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

_logo = "icon.png"
_references = ['you2019']
__version__ = "3.0.0"

MEMBRAIN_ENV_VAR = "MEMBRAIN_ENV"
DEFAULT_MEMBRAIN_ENV ="MemBrain"

class Plugin(pwem.Plugin):
    
    @classmethod
    def _defineVariables(cls):
        """ Defines variables for this plugin. scipion3 config -p membrain will show them with current values"""
        cls._defineVar(MEMBRAIN_ENV_VAR, DEFAULT_MEMBRAIN_ENV)

    @classmethod
    def getMemBrainActivation(cls):
        return "conda activate " + cls.getVar(MEMBRAIN_ENV_VAR)

    @classmethod
    def getProgram(cls, program):
        """ Return the full command to run a memBrain program. """
        cmd = '%s %s && ' % (cls.getCondaActivationCmd(), cls.getMemBrainActivation())
        return cmd + program

    @classmethod
    def defineBinaries(cls, env):

        installed = "memBrainInstalled.txt"
        membrain_commands = []
        membrain_commands.append(("git clone https://github.com/CellArchLab/MemBrain.git", "MemBrain"))
        membrain_commands.append(("cd MemBrain && " + cls.getCondaActivationCmd() + "conda env create -f MemBrain_requirements.yml && touch " + installed, os.path.join("MemBrain", installed)))

        env.addPackage('membrain', version=1.0,
                       commands=membrain_commands,
                       tar=VOID_TGZ,
                       default=True)
