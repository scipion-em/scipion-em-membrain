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

import pwem

MEMBRAIN_SEG = 'membrain-seg'
MEMBRAIN_SEG_VERSION = '0.0.1'

# Use this variable to activate an environment from the Scipion conda
MEMBRAIN_SEG_ENV_VAR = "MEMBRAIN_SEG_ENV"
DEFAULT_MEMBRAIN_SEG_ENV = "membrain-seg-scipion"

# models
MODEL_VERSION = '10'
MODEL_PKG_NAME = 'membrain_seg_models'
MEMBRAIN_SEG_MODEL_VAR = 'MEMBRAIN_SEG_MODEL'
MEMBRAIN_SEG_MODEL = 'MemBrain_seg_v10_alpha.ckpt'
DEFAULT_MEMBRAIN_SEG_MODEL = pwem.Config.EM_ROOT
DEFAULT_MEMBRAIN_SEG_MODEL += "/" + MODEL_PKG_NAME + "-" + MODEL_VERSION
DEFAULT_MEMBRAIN_SEG_MODEL += "/" + MEMBRAIN_SEG_MODEL
GDRIVE_FILEID = '1tSQIz_UCsQZNfyHg0RxD-4meFgolszo8'
