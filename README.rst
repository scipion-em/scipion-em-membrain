===========================
Membrain plugin for Scipion
===========================

This plugin implements protocols from the MemBrain_ family of software packages for analysis of membrane proteins in cryo-electron tomography.

Installation
------------
The plugin is currently only available in development mode. To install, proceed with the following steps:

**Clone this repo:**

.. code-block::

    git clone https://github.com/scipion-em/scipion-em-membrain.git

**Install this plugin in devel (editable) mode:**

.. code-block::

    scipion3 installp -p /path/to/scipion-em-membrain --devel

Scipion will automatically install MemBrain and download any pre-trained models necessary for running it.

Configuration variables
.......................

There are some variables related to the MemBrain installation. For example, if you have installed
MemBrain-seg outside of Scipion, you may define ``MEMBRAIN_SEG_ENV_ACTIVATION`` for specifying
how to activate the environment.

.. code-block::

    MEMBRAIN_SEG_ENV_ACTIVATION="conda activate membrain-seg"

If this variable is not defined, a default value will be provided that will work with the
latest version installed.

Likewise, you can use an environment variable to point to a MemBrain-seg model downloaded externally:

.. code-block::

    MEMBRAIN_SEG_MODEL="/path/to/membrain-seg/model.ckpt"

Protocols
---------
The following protocols are currently implemented:

* Membrane segmentation using MemBrain-seg_

Using GPU or CPU
................
By default, MemBrain protocols assume that a GPU card is available. If such a device is not found, protocols may still run using the CPU with parallel threads, but will be much slower.

References
----------
* Lamm, Lorenz, Ricardo D. Righetto, Wojciech Wietrzynski, Matthias Pöge, Antonio Martinez-Sanchez, Tingying Peng, and Benjamin D. Engel. "MemBrain: A deep learning-aided pipeline for detection of membrane proteins in Cryo-electron tomograms." *Computer methods and programs in biomedicine* 224 (2022): 106990.

Contact information
-------------------

If you experiment any problem, please contact us here: scipion-users@lists.sourceforge.net or open an issue_.

We'll be pleased to help.

*Scipion Team*

.. _issue: https://github.com/scipion-em/scipion-em-membrain/issues
.. _MemBrain: https://doi.org/10.1016/j.cmpb.2022.106990
.. _MemBrain-seg: https://github.com/teamtomo/membrain-seg
