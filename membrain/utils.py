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
Utilities for MemBrain protocols
'''


def getGoodGpuList(gpu_list):
    # gpu_list can be specified both comma-separated or space-separated.
    # Users can introduce arbitrary number of blank spaces in between.
    # So we need to sanitize it:

    good_gpus = []  # Safe GPU list will be stored here as list of strings
    if ',' in gpu_list:
        for gpu in gpu_list.split(','):  # First split by commas
            # Sanitize any blank  spaces and append
            good_gpus.append(' '.join(gpu.split()))
    else:
        # If not comma separated we start sanitizing extra blank spaces
        gpu_list = ' '.join(gpu_list.split())
        # Then a simple split by blank will do
        for gpu in gpu_list.split(' '):
            good_gpus.append(gpu)

    return good_gpus
