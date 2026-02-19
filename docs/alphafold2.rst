AlphaFold2
==========

This section covers **AlphaFold2** protein structure prediction on HPC
clusters. It describes what HPC admins need to be aware of from the official
AlphaFold2 installation and runtime requirements, and how TACC provides
AlphaFold2 via a container and module file (e.g. on Lonestar6).

What is AlphaFold2?
-------------------

`AlphaFold2 <https://github.com/google-deepmind/alphafold>`_ is Google
DeepMind's deep learning system for predicting the three-dimensional structure
of proteins from their amino acid sequences. The open-source code implements
the inference pipeline of AlphaFold v2 (often called AlphaFold or AlphaFold2).
It also supports **AlphaFold-Multimer** for protein complexes (multiple
chains in one FASTA).

* The code is licensed under Apache 2.0; model parameters
  are made available under CC BY 4.0.
* Input is one or more FASTA files
* The pipeline runs MSA (multiple sequence alignment) and template search,
  then neural-network inference to produce predicted structures (e.g. PDB,
  pLDDT, and optional pTM/PAE)

Why it's relevant
-----------------

For HPC clusters that serve structural biology or biochemistry users,
AlphaFold2 is often requested for:

* **Protein structure prediction** — single chains (monomer) or complexes
  (multimer) from FASTA sequences.
* **Reproducing or extending published work** — many papers report AlphaFold
  models and depositions.
* **Hypothesis generation** — before wet-lab experiments or as part of
  integrative modeling pipelines.

Supporting AlphaFold2 means providing a container or module environment,
access to genetic databases and model parameters, and clear guidance on GPU
partitions, walltime, and storage.

Why this matters for HPC admins
---------------------------------

The following points are drawn from the official `AlphaFold2 installation and
running your first prediction
<https://github.com/google-deepmind/alphafold?tab=readme-ov-file#installation-and-running-your-first-prediction>`_
section and related documentation.

1. **Operating system**: 
   
   AlphaFold runs on Linux only; other operating
   systems are not supported.

2. **Disk space**: 
   
   Full installation requires **up to 3 TB of disk space** to
   hold genetic databases. 
  
  * SSD storage is recommended for better genetic search performance. 
  * The download size is about **556 GB**; when unzipped, the total is about **2.62 TB**. 
  * If using the reduced databases preset (``--db_preset=reduced_dbs``), 
    roughly **600 GB** of disk space is needed,
    with lower CPU/RAM requirements (8 vCPUs, 8 GB RAM).

3. **GPU**: 
   
  * A modern NVIDIA GPU is highly recommended for inference. GPUs with more
    memory can predict larger protein structures. Admins should document partition selection
    and CUDA/driver compatibility.
  * You can run AlphaFold2 without a GPU (with the ``--use_gpu=False`` flag), 
    but it will be much slower. 
  * AlphaFold2 is set up to use only **one** GPU per single prediction (i.e., it does not split 
    one model inference across GPUs). If your node has two GPUs, for example, and you want to make sure 
    both GPUs "do work", you must run **two independent AlphaFold2 runs at the same time**. 

4. **Containers**:
   
   The standard way to run AlphaFold2 is via **Docker** with
   the **NVIDIA Container Toolkit** for GPU support. On HPC systems that use
   **Singularity/Apptainer** instead of Docker, third-party Singularity setups
   are commonly used (the AlphaFold repo links to issues such as `#10
   <https://github.com/google-deepmind/alphafold/issues/10>`_ and `#24
   <https://github.com/google-deepmind/alphafold/issues/24>`_ for examples).
   Database paths and bind mounts (data directory, output directory) must be
   configured so the container can read genetic databases and write results.

5. **Genetic databases**: 
  
  AlphaFold2 needs multiple genetic (sequence) databases:
  BFD (or small_bfd for reduced_dbs), MGnify, PDB70, PDB (mmCIF), PDB seqres
  (for Multimer), UniRef30, UniProt (for Multimer), UniRef90. The
  ``scripts/download_all_data.sh`` script can download and set up full or
  reduced databases. **Permissions**: If the download directory does not have
  full read/write permissions, MSA tools can fail with opaque errors; the docs
  suggest ``chmod 755 --recursive "$DOWNLOAD_DIR"`` if needed.

6. **Model parameters**:
  
  Model parameters are downloaded as part of
  ``download_all_data.sh`` (or via ``scripts/download_alphafold_params.sh``).
  They are distributed under CC BY 4.0. Sites that redistribute the
  container may still need to ensure parameters are present in the data
  directory or bind-mounted correctly.

7. **Memory and I/O**:
  
  MSA and template search are CPU- and disk-intensive.
  Running from a fast filesystem (e.g. scratch) and ensuring
  sufficient RAM (32 GB minimum; 64 GB recommended for large proteins or multiple jobs).
  Output directory should be an absolute path with write permissions.

8. **CUDA**:

  CUDA version 11.3 or higher required. 

Installations and access at TACC
---------------------------------

TACC provides AlphaFold2 as a **container image** plus a **Lua module file**
that exposes a single entry point so users do not need to invoke Apptainer
directly.

**Container**

* Container Image: `tacc/alphafold:2.3.2 <https://hub.docker.com/r/tacc/alphafold/tags>`_
* On the cluster, the image is built as an Apptainer SIF, e.g., 
  ``/scratch/tacc/apps/bio/alphafold/2.3.2/images/alphafold_2.3.2.sif``
* The container’s main script is ``/app/run_alphafold.sh``, which is
  invoked with arguments (e.g. FASTA paths, data dir, output dir) as
  documented by TACC and the AlphaFold2 repo.

**Module file**

The module file sets the environment and defines a shell function
``run_alphafold.sh`` that runs the container with **GPU support** (``--nv``)
and passes through any user arguments. Example Lua content (as used at TACC):

.. code-block:: lua

  local help_message = [[
  This is a module file for the container tacc/alphafold:2.3.2, which exposes the
  following program:

  - run_alphafold.sh

  This container was pulled from:

    https://hub.docker.com/r/tacc/alphafold

  If you encounter errors in alphafold or need help running the
  tools it contains, please find supporting documentation at:

    https://portal.tacc.utexas.edu/software/alphafold

  ]]

  help(help_message,"\\n")

  -- Environment vars
  whatis("Name: alphafold")
  whatis("Version: 2.3.2")
  whatis("Category: Unknown")
  whatis("Keywords: Container")
  whatis("Description: The alphafold package")
  whatis("URL: https://github.com/google-deepmind/alphafold")
  setenv("AF2_HOME", "/scratch/tacc/apps/bio/alphafold/2.3.2")

  -- Shell function
  set_shell_function("run_alphafold.sh", 
  "apptainer exec --nv " ..
  " /scratch/tacc/apps/bio/alphafold/2.3.2/images/alphafold_2.3.2.sif " ..
  " /app/run_alphafold.sh $@",
  -- C-shell version 
  "apptainer exec --nv " ..
  " /scratch/tacc/apps/bio/alphafold/2.3.2/images/alphafold_2.3.2.sif " ..
  " /app/run_alphafold.sh $*")

  -- Load dependencies
  always_load("tacc-apptainer")
  try_load("cuda/11.4")

**What this does**

* ``set_shell_function("run_alphafold.sh", ...)``: 
  
  Defines the command ``run_alphafold.sh`` so that when users run it 
  (with their FASTA paths, output dir, etc.), the module invokes 
  ``apptainer exec --nv`` with the correct SIF path and the container’s 
  ``/app/run_alphafold.sh``, passing ``$@`` (Bash) or ``$*`` (C-shell).

* ``setenv("AF2_HOME", ...``):
  
  Sets the AlphaFold2 install root; scripts or
  docs can reference ``$AF2_HOME`` for the image path or related data.

* ``always_load("tacc-apptainer")``:
  
  Ensures the Apptainer environment is loaded.

* ``try_load("cuda/11.4")``:
  
  Loads a CUDA version compatible with the
  container’s GPU stack; ``--nv`` then exposes the GPU to the container.

Users load the module (e.g. ``module load alphafold/2.3.2-ctr``), then run
``run_alphafold.sh`` with the arguments expected by the TACC/AlphaFold2
wrapper (typically including paths to FASTA files, the genetic database
directory, and the output directory). 

Running AlphaFold2 
------------------

Structure Prediction from Single Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To perform 3D protein structure prediction with AlphaFold2, first upload or create a fasta-formatted protein 
primary sequence to your ``$WORK`` or ``$SCRATCH`` (recommended) space. A valid fasta sequence might look like:

.. code-block:: text

  >sample1 
  GDKERVDENVCWCKLWLWNMRAPTASGEMWKIKVAYQHCWRAVCFSFETVGANKDMHEKC
  DKWAANMEEFGLMANMRWIDSTMKYFTFHVDAAQLGRFKDKMPDQPRPKQVHVDRFALFF
  FYGILMHGTDANREANLLCNVRFAVLFGWANANPMDDVYHMGHHPRLYQVPNIFDYNDWL
  FWGLFKIIPPVYGGITWDMNKDTTRRWLHVMERSATYEPQSRRILGCIGWSFGMRPGQEH
  GHMHQFCLEFGNTYDNFFNSEEELPKQFRYMRPGHGMEQQSCEWVFCVDKDYPWIGTTWM

Next, prepare a batch job submission script for running AlphaFold2. Two different templates for different levels of precision 
are provided: 

1. ``full_dbs.slurm``: high precision (default)

.. code-block:: bash

  #!/bin/bash
  # full_dbs.slurm
  # -----------------------------------------------------------------
  #SBATCH -J af2_full                   # Job name
  #SBATCH -o af2_full.o%j               # Name of stdout output file
  #SBATCH -e af2_full.e%j               # Name of stderr error file
  #SBATCH -p gpu-a100                   # Queue (partition) name
  #SBATCH -N 1                          # Total # of nodes 
  #SBATCH -t 12:00:00                   # Run time (hh:mm:ss)
  #SBATCH -A <your-allocation>          # Project/Allocation name 
  # -----------------------------------------------------------------

  # Load modules
  module use /scratch/tacc/apps/bio/alphafold/modulefiles
  module load alphafold/2.3.2-ctr

  # Run AlphaFold2
  run_alphafold.sh --flagfile=$AF2_HOME/examples/flags/full_dbs.ff \
                   --fasta_paths=$SCRATCH/input/sample.fasta \
                   --output_dir=$SCRATCH/output \
                   --model_preset=monomer \
                   --max_template_date=2050-01-01 \
                   --use_gpu_relax=True

1. ``reduced_dbs.slurm``: higher speed 

.. code-block:: bash

  #!/bin/bash
  # reduced_dbs.slurm
  # -----------------------------------------------------------------
  #SBATCH -J af2_reduced                # Job name
  #SBATCH -o logs/%x-%j.out             # Name of stdout output file
  #SBATCH -e logs/%x-%j.err             # Name of stderr error file
  #SBATCH -p gpu-a100                   # Queue (partition) name
  #SBATCH -N 1                          # Total # of nodes 
  #SBATCH -n 1                          # Total # of mpi tasks 
  #SBATCH -t 12:00:00                   # Run time (hh:mm:ss)
  #SBATCH -A <your-allocation>          # Project/Allocation name 
  # -----------------------------------------------------------------

  # Load modules
  module use /scratch/tacc/apps/bio/alphafold/modulefiles
  module load alphafold/2.3.2-ctr

  echo -n "starting at: "
  date

  # Run AlphaFold2
  run_alphafold.sh --flagfile=$AF2_HOME/examples/flags/reduced_dbs.ff \
                   --fasta_paths=$SCRATCH/input/sample.fasta \
                   --output_dir=$SCRATCH/output \
                   --model_preset=monomer \
                   --max_template_date=2050-01-01 \
                   --use_gpu_relax=True

  echo -n "starting at: "
  date

The ``flagfile`` is a configuration file passed to AlphaFold2 containing parameters including the 
level of precision, the location of the databases for multiple sequence alignment, and more. The default flag 
files used at TACC can be found in our `GitHub alphafold-config repo <https://github.com/user/alphafold-config/tree/main/ls6/2.3.2/examples/flags>`_, 
and typically these should not be edited. 

The other three parameters passed to AlphaFold2 should be customized by your input path / filename, desired output path, and the 
selection of models. These parameters are summarized below:

.. list-table::
    :align: center
    :header-rows: 1

    * - Parameter
      - Setting
      - Example
    * - ``--fasta_paths``
      - Full path including filename to your test data
      - ``=$SCRATCH/input/sample.fasta``
    * - ``--output_dir``
      - Full path to desired output dir (/scratch filesystem) 
      - ``=$SCRATCH/output``
    * - ``model_preset``
      - Control which AlphaFold2 model to run, options are
      - ``=monomer | =monomer_casp14 | =monomer_ptm | =multimer``
    * - ``--max_template_date``
      - Control which structures from PDB are used
      - ``=2050-01-01`` (all)
    * - ``--use_gpu_relax``
      - Whether to relax on GPUs (recommended if GPU available) 
      - ``=True | =False``

Using multiple GPUs on a node
+++++++++++++++++++++++++++++

AlphaFold2 uses **only one GPU per run**; it does not split a single prediction across GPUs. 
To utilize two (or more) GPUs on the same node, run **two independent AlphaFold2 runs 
at the same time**, each with its own input and output.

In the job script, launch two ``run_alphafold.sh`` processes in parallel, each bound to a different 
GPU via ``CUDA_VISIBLE_DEVICES``, 
and use **different** ``--fasta_paths`` and ``--output_dir`` so they do not overwrite each other.
Example pattern:

.. code-block:: bash


  module load alphafold/2.3.2-ctr

  # Run two predictions in parallel, one per GPU
  CUDA_VISIBLE_DEVICES=0 run_alphafold.sh --flagfile=$AF2_HOME/examples/flags/reduced_dbs.ff \
                                          --fasta_paths=$SCRATCH/input/sample1.fasta \
                                          --output_dir=$SCRATCH/output/sample1 \
                                          --model_preset=monomer \
                                          --max_template_date=2020-05-14 \
                                          --use_gpu_relax=True &
  CUDA_VISIBLE_DEVICES=1 run_alphafold.sh --flagfile=$AF2_HOME/examples/flags/reduced_dbs.ff \
                                          --fasta_paths=$SCRATCH/input/sample2.fasta \
                                          --output_dir=$SCRATCH/output/sample2 \
                                          --model_preset=monomer \
                                          --max_template_date=2020-05-14 \
                                          --use_gpu_relax=True &

  wait

**Notes for admins**

* **CPU and RAM**: Running two predictions on one node roughly doubles CPU and memory use 
  during MSA and inference. Ensure the partition’s per-node resources (e.g. 64 GB RAM or 
  more for two full-database runs) are sufficient, or recommend reduced databases when running 
  two at once.
* **GPU binding**: If you do not set ``CUDA_VISIBLE_DEVICES``, both processes may default 
  to GPU 0. Pin each run to a specific GPU (e.g. ``CUDA_VISIBLE_DEVICES=0`` and 
  ``CUDA_VISIBLE_DEVICES=1``) so the two runs use different devices.

Output 
------

AlphaFold2 generates multiple output files for each prediction.
Here is what the output directory for one fasta sequence looks like: 

.. code-block:: console

  $ ls -lh 

  total 31M
  -rw------- 1 user group 1.1K Feb 16 23:00 confidence_model_1_pred_0.json
  -rw------- 1 user group 1.1K Feb 16 23:02 confidence_model_2_pred_0.json
  -rw------- 1 user group 1.1K Feb 16 23:03 confidence_model_3_pred_0.json
  -rw------- 1 user group 1.1K Feb 16 23:03 confidence_model_4_pred_0.json
  -rw------- 1 user group 1.1K Feb 16 23:04 confidence_model_5_pred_0.json
  -rw------- 1 user group 5.1M Feb 16 22:59 features.pkl
  drwx------ 2 user group    4 Feb 16 22:58 msas/
  -rw------- 1 user group  52K Feb 16 23:04 ranked_0.cif
  -rw------- 1 user group  98K Feb 16 23:04 ranked_0.pdb
  -rw------- 1 user group  52K Feb 16 23:04 ranked_1.cif
  -rw------- 1 user group  48K Feb 16 23:04 ranked_1.pdb
  -rw------- 1 user group  52K Feb 16 23:04 ranked_2.cif
  -rw------- 1 user group  48K Feb 16 23:04 ranked_2.pdb
  -rw------- 1 user group  52K Feb 16 23:04 ranked_3.cif
  -rw------- 1 user group  48K Feb 16 23:04 ranked_3.pdb
  -rw------- 1 user group  52K Feb 16 23:04 ranked_4.cif
  -rw------- 1 user group  48K Feb 16 23:04 ranked_4.pdb
  -rw------- 1 user group  400 Feb 16 23:04 ranking_debug.json
  -rw------- 1 user group  52K Feb 16 23:04 relaxed_model_4_pred_0.cif
  -rw------- 1 user group  98K Feb 16 23:04 relaxed_model_4_pred_0.pdb
  -rw------- 1 user group 1.4K Feb 16 23:04 relax_metrics.json
  -rw------- 1 user group 4.9M Feb 16 23:00 result_model_1_pred_0.pkl
  -rw------- 1 user group 4.9M Feb 16 23:02 result_model_2_pred_0.pkl
  -rw------- 1 user group 4.9M Feb 16 23:03 result_model_3_pred_0.pkl
  -rw------- 1 user group 4.9M Feb 16 23:03 result_model_4_pred_0.pkl
  -rw------- 1 user group 4.9M Feb 16 23:04 result_model_5_pred_0.pkl
  -rw------- 1 user group  681 Feb 16 23:04 timings.json
  -rw------- 1 user group  52K Feb 16 23:00 unrelaxed_model_1_pred_0.cif
  -rw------- 1 user group  48K Feb 16 23:00 unrelaxed_model_1_pred_0.pdb
  -rw------- 1 user group  52K Feb 16 23:02 unrelaxed_model_2_pred_0.cif
  -rw------- 1 user group  48K Feb 16 23:02 unrelaxed_model_2_pred_0.pdb
  -rw------- 1 user group  52K Feb 16 23:03 unrelaxed_model_3_pred_0.cif
  -rw------- 1 user group  48K Feb 16 23:03 unrelaxed_model_3_pred_0.pdb
  -rw------- 1 user group  52K Feb 16 23:03 unrelaxed_model_4_pred_0.cif
  -rw------- 1 user group  48K Feb 16 23:03 unrelaxed_model_4_pred_0.pdb
  -rw------- 1 user group  52K Feb 16 23:04 unrelaxed_model_5_pred_0.cif
  -rw------- 1 user group  48K Feb 16 23:04 unrelaxed_model_5_pred_0.pdb

**Most important files:**

* ``ranked_0.pdb`` / ``randed_0.cif``: Best relaxed prediction (primary output), ranked by confidence scores (pLDDT)
* ``confidence_model_*_pred_0.json``: Per-residue confidence scores (pLDDT)

**Structure files**: 

* ``relaxed_model_*_pred_0.pdb``: Energy-minimized structures (better stereochemistry)
* ``unrelaxed_model_*_pred_0.pdb``: Raw predictions from each of the 5 models (useful for comparing diversity)

**Intermediate/advanced files**: 

* ``result_model_*_pred_0.pkl``: Full prediction results (for advanced analysis)
* ``features.pkl``: MSA and template features
* ``msas/``: Multiple sequence alignments directory 

**Metadata:**

* ``timings.json``: Pipeline timing breakdown 
* ``relax_metrics.json``: Relaxation step metrics
* ``ranking_debug.json``: Model ranking debug info 


Additional resources
--------------------

* AlphaFold2: `Google DeepMind AlphaFold2 (open source code)
  <https://github.com/google-deepmind/alphafold>`_
* AlphaFold2: `Installation and running your first prediction
  <https://github.com/google-deepmind/alphafold?tab=readme-ov-file#installation-and-running-your-first-prediction>`_
* TACC: `AlphaFold at TACC <https://docs.tacc.utexas.edu/software/alphafold/>`_
* Docker image: `tacc/alphafold <https://hub.docker.com/r/tacc/alphafold>`_
