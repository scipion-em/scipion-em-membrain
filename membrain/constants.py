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
MEMBRAIN_SEG_HOME = 'MEMBRAIN_SEG_HOME'
MODEL_MODELS_HOME = 'MODEL_MODELS_HOME'
MEMBRAIN_SEG = 'membrain-seg'
MEMBRAIN_SEG_MODELS_DIR = 'membrain_seg_models'
MEMBRAIN_SEG_VERSION = '0.0.10'

# Use this variable to activate an environment from the Scipion conda
MEMBRAIN_SEG_ENV_VAR = "MEMBRAIN_SEG_ENV"
MEMBRAIN_SEG_ENV_DEFAULT = f"membrain-seg-{MEMBRAIN_SEG_VERSION}"
MEMBRAIN_SEG_ENV_ACTIVATION_VAR = "MEMBRAIN_SEG_ENV_ACTIVATION"
MEMBRAIN_SEG_ENV_ACTIVATION_DEFAULT = "conda activate " + MEMBRAIN_SEG_ENV_DEFAULT

# models
MEMBRAIN_SEG_MODEL_VAR = 'MEMBRAIN_SEG_MODEL'
MEMBRAIN_SEG_MODEL_NAME_DEFAULT = 'MemBrain_seg_v10_beta.ckpt'
GDRIVE_FILEID = '1hruug1GbO4V8C4bkE5DZJeybDyOxZ7PX'

# Outputs
OUTPUT_TOMOMASK_NAME = 'tomoMasks'
