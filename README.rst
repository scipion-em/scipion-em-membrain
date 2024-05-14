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

There are some *optional* variables related to the MemBrain installation. For example, if you have installed MemBrain-seg outside of Scipion, you may define ``MEMBRAIN_SEG_ENV_ACTIVATION`` in your ``scipion.conf`` file for specifying an already existing conda environment or a script to be sourced:

.. code-block::

    MEMBRAIN_SEG_ENV_ACTIVATION = conda activate my-membrain-seg-env

Also, you can use the ``MEMBRAIN_SEG_MODEL`` environment variable to indicate the **full path** to a MemBrain-seg model downloaded externally:

.. code-block::

    MEMBRAIN_SEG_MODEL = /path/to/membrain-seg/model.ckpt

If these variables are not defined, default values will be used that will work with the
latest version installed through Scipion.

Protocols
---------
The following protocols are currently implemented:

* Membrane segmentation using the **MemBrain-seg** module

Using GPU or CPU
................
By default, MemBrain protocols assume that a GPU card is available. If such a device is not found, protocols may still run using the CPU with parallel threads, but will be much slower.

References
----------

<!-- in JSB citation style: -->

* Lamm, L., Zufferey, S., Righetto, R.D., Wietrzynski, W., Yamauchi, K.A., Burt, A., Liu, Y., Zhang, H., Martinez-Sanchez, A., Ziegler, S., Isensee, F., Schnabel, J.A., Engel, B.D., Peng, T., 2024. MemBrain v2: an end-to-end tool for the analysis of membranes in cryo-electron tomography. https://doi.org/10.1101/2024.01.05.574336 

* Lamm, L., Righetto, R.D., Wietrzynski, W., Pöge, M., Martinez-Sanchez, A., Peng, T., Engel, B.D., 2022. MemBrain: A deep learning-aided pipeline for detection of membrane proteins in Cryo-electron tomograms. Computer Methods and Programs in Biomedicine 224, 106990. https://doi.org/10.1016/j.cmpb.2022.106990


Contact information
-------------------

If you experiment any problem, please contact us here: scipion-users@lists.sourceforge.net or open an issue_.

We'll be pleased to help.

*Scipion Team*

.. _issue: https://github.com/scipion-em/scipion-em-membrain/issues
.. _MemBrain: https://doi.org/10.1101/2024.01.05.574336
