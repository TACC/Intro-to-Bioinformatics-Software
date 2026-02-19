AlphaFold3
==========

This section covers **AlphaFold3** macromolecular structure
prediction on HPC clusters. It describes what HPC admins need to be 
aware of from the official AlphaFold3 installation and runtime requirements, 
and how TACC provides AlphaFold3 via a container and module file (e.g. 
on Lonestar6).

What is AlphaFold3?
------------------

`AlphaFold3 <https://github.com/google-deepmind/alphafold3>`_ is Google 
DeepMind's deep learning system for predicting the three-dimensional structure of 
proteins and other biological macromoleculesfrom their amino acid (or nucleotide) 
sequences. 
**AlphaFold3** (2024) extends the approach of 
`AlphaFold2 <https://github.com/google-deepmind/alphafold>`_ 
(2021) to predict the structure and interactions of proteins,
nucleic acids, small molecules, ions, and post-translational modifications in
complexes. It also represents a significant improvement in protein structure 
prediction over AlphaFold2. 

The source code is available on GitHub, and AlphaFold3 depends on
roughly 630 GB of disk space to keep genetic databases for querying 
(SSD storage is recommended). 

In addition, AlphaFold3 requires an NVIDIA GPU with Compute Capability 8.0 or 
greater. GPUs with more memory can predict larger protein structures. 
It is recommended to have at least 64 GB of RAM. 

* The code is licensed under CC-BY-NC-SA 4.0; the AlphaFold3 model parameters and 
  output are **only** available for non-commercial use only. You **must not** use nor 
  allow others to use:

  * AlphaFold3 model parameters or output for any **commercial** activities
  * AlphaFold3 output to **train machine learning models** or releated technology
  
* Do not publish or share AlphaFold3 model parameters – have your users fill out 
  `this form <https://docs.google.com/forms/d/e/1FAIpQLSfWZAgo1aYk0O4MuAXZj8xRQ8DafeFJnldNOnh_13qAx2ceZw/viewform>`_
  to obtain the model parameters
* Installation instructions are `here <https://github.com/google-deepmind/alphafold3/blob/main/docs/installation.md>`_
* `Input <https://github.com/google-deepmind/alphafold3/blob/main/docs/input.md>`_ is one or more JSON files 
* The pipeline runs **MSA (multiple sequence alignment) and template search** (data pipeline, can run on CPU), 
  then **neural-network inference** (requires GPU) to produce predicted structures (e.g. PDB, CIF, 
  confidence scores). The data pipeline and inference steps can be run separately using ``--norun_inference`` 
  and ``--norun_data_pipeline`` flags.


Why it's relevant
-----------------

For HPC clusters that serve structural biology or biochemistry users, AlphaFold3
is often requested for:

* **Multi-molecule structure prediction** — Unlike AlphaFold2 (proteins only),
  AlphaFold3 predicts structures of **proteins, nucleic acids (DNA/RNA), small
  molecules, ions, and post-translational modifications** in complexes. This
  enables modeling of protein–DNA, protein–RNA, protein–ligand, and other
  multi-component systems.
* **Improved protein structure accuracy** — AlphaFold3 represents a significant
  improvement over AlphaFold2 for protein structure prediction, making it
  preferred for new projects when available.
* **Complex interaction modeling** — Predicts how different molecule types
  interact (e.g. transcription factors with DNA, enzymes with cofactors or
  substrates, ribonucleoprotein complexes).
* **Hypothesis generation** — Before wet-lab experiments or as part of
  integrative modeling pipelines, particularly for systems involving multiple
  molecule types.

**Key differences from AlphaFold2:**

* **Input format**: JSON files (not FASTA) that can specify multiple molecule
  types and their relationships.
* **Scope**: Handles nucleic acids, small molecules, ions, and PTMs in addition
  to proteins.
* **Accuracy**: Improved protein structure prediction compared to AlphaFold2.
* **Licensing**: Non-commercial use only (CC-BY-NC-SA 4.0); model parameters
  must be requested separately and cannot be redistributed.

Supporting AlphaFold3 means providing a container or module environment, access
to reference databases, clear guidance on GPU partitions and walltime, and
clear guidelines regarding licensing restrictions and the model-parameter
request process (users must obtain parameters from Google).

Why this matters for HPC admins
-------------------------------

The following points are drawn from the official `AlphaFold3 installation
<https://github.com/google-deepmind/alphafold3/blob/main/docs/installation.md>`_
section and related documentation.

1. **Operating system**: 
   
   AlphaFold3 runs on **Linux only**; other operating systems are not supported.

2. **Disk space**: 
   
   Full installation requires **up to 1 TB of disk space** to hold genetic databases.
   
   * **Download size**: Approximately **252 GB** for the full databases.
   * **Unzipped size**: Approximately **630 GB** when decompressed.
   * **SSD storage is recommended** for better genetic search performance.
   * The download directory should **not** be a subdirectory of the AlphaFold3 repository
     directory (to avoid slow Docker builds).

3. **GPU**: 
   
   * An **NVIDIA GPU with Compute Capability 8.0 or greater** is required (e.g. A100, H100).
     GPUs with more memory can predict larger structures.
   * Verified: Inputs with up to **5,120 tokens** can fit on a single NVIDIA A100 80 GB
     or a single NVIDIA H100 80 GB.
   * AlphaFold3 inference requires GPUs; the data pipeline (MSA and template search)
     can run on CPU.

4. **Memory (RAM)**:
   
   **At least 64 GB RAM recommended**, especially for long targets where the genetic
   search stage can consume significant memory.

5. **CUDA**:
   
   The Docker container requires that the host machine has **CUDA 12.6** installed.
   For local installations outside Docker, ensure CUDA, cuDNN, and JAX are correctly
   installed.

6. **Containers**:
   
   AlphaFold3 is typically run via **Docker** with the **NVIDIA Container Toolkit** for
   GPU support, or **Singularity/Apptainer** on HPC systems. Database paths and bind
   mounts (input, output, model parameters, public databases) must be configured correctly;
   the TACC module and `alphafold3-config <https://github.com/kbeavers/alphafold3-config>`_
   repo define these for TACC systems.

7. **Genetic databases**: 
   
   AlphaFold3 needs multiple genetic (sequence) databases: BFD small, MGnify, PDB (mmCIF),
   PDB seqres, UniProt, UniRef90, NT (nucleotide), RFam, and RNACentral. The
   ``fetch_databases.sh`` script downloads and sets up all databases. **Permissions**: If
   the download directory does not have full read/write permissions, MSA tools can fail
   with opaque errors; the docs suggest ``chmod 755 --recursive "$DOWNLOAD_DIR"`` if needed.

8. **Model parameters**:
   
   Model parameters are **not redistributable** by HPC sites. Users must request access
   via the `AlphaFold3 Model Request Form
   <https://forms.gle/svvpY4u2jsHEwWYS6>`_ and download them directly from Google.
   Document this clearly and point users to the request process. Parameters should be
   placed in a directory outside the AlphaFold3 repository directory (we recommend users 
   put model parameters in their $HOME or $WORK directories).

9. **Storage and I/O**:
   
   Running from a fast filesystem (e.g. scratch) is recommended. 

Installations and access at TACC
--------------------------------

TACC provides AlphaFold3 as a **container image** plus a **Lua module file**
that exposes a single entry point so users do not need to invoke Apptainer
directly. Data (databases) and examples live on shared paths; **model parameters
are not included**—users must obtain them from Google and set
``AF3_MODEL_PARAMETERS_DIR`` to their own copy.

**Container**

* Container Image: `tacc/alphafold3:3.0.1 <https://hub.docker.com/r/tacc/alphafold3>`_
* On the cluster, the image is built as an Apptainer SIF, e.g.,
  ``/scratch/tacc/apps/bio/alphafold3/3.0.1/images/alphafold3_3.0.1.sif``
* The container is invoked via a wrapper that runs AlphaFold3 with the correct
  bind mounts for input, output, model parameters, and public databases (e.g.
  ``run_alphafold.py`` with ``--json_path``, ``--model_dir``, ``--db_dir``,
  ``--output_dir`` as documented by TACC and the AlphaFold3 repo).

**Module file**

The module file sets the environment and defines a shell function
``run_alphafold3`` that runs the container with **GPU support** (``--nv``)
and passes through any user arguments. Example Lua content (as used at TACC):

.. code-block:: lua

  local help_message = [[
  This is a module file for the container tacc/alphafold:3.0.1, which exposes the
  following program:

  - run_alphafold3

  This command launches AlphaFold3 inside an Apptainer container using GPU support.
  You must define the following variables before running:
  
    export AF3_INPUT_DIR=/your/json/dir
    export AF3_OUTPUT_DIR=/your/output/dir
    export AF3_MODEL_PARAMETERS_DIR=/your/model/parameters/dir

  This container was pulled from:

    https://hub.docker.com/r/tacc/alphafold3

  If you encounter errors in alphafold or need help running the
  tools it contains, please find supporting documentation at:

    https://portal.tacc.utexas.edu/software/alphafold3

  ]]

  help(help_message, "\n")

  whatis("Name: alphafold3")
  whatis("Version: 3.0.1-f3e86f2")
  whatis("Category: Bioinformatics")
  whatis("Keywords: Container, AlphaFold3")
  whatis("Description: AlphaFold3 run environment using TACC container image.")
  whatis("URL: https://github.com/google-deepmind/alphafold3")

  -- Environment vars
  setenv("AF3_HOME", "/scratch/tacc/apps/bio/alphafold3/3.0.1")
  setenv("AF3_IMAGE", "/scratch/tacc/apps/bio/alphafold3/3.0.1/image/alphafold3_3.0.1-f3e86f2.sif")
  setenv("AF3_CODE_DIR", "/scratch/tacc/apps/bio/alphafold3/3.0.1/code_TEST")
  setenv("AF3_DATABASES_DIR", "/scratch/tacc/apps/bio/alphafold3/3.0.1/data")

  -- Load dependencies
  always_load("tacc-apptainer")
  try_load("cuda/12.2")

  -- Shell function
  set_shell_function("run_alphafold3",
  "apptainer exec --nv " ..
  "  ${XLA_PYTHON_CLIENT_PREALLOCATE:+--env XLA_PYTHON_CLIENT_PREALLOCATE=$XLA_PYTHON_CLIENT_PREALLOCATE } " ..
  "  ${TF_FORCE_UNIFIED_MEMORY:+--env TF_FORCE_UNIFIED_MEMORY=$TF_FORCE_UNIFIED_MEMORY } " ..
  "  ${XLA_CLIENT_MEM_FRACTION:+--env XLA_CLIENT_MEM_FRACTION=$XLA_CLIENT_MEM_FRACTION } " ..
  "  --bind $AF3_INPUT_DIR:/root/af_input " ..
  "  --bind $AF3_OUTPUT_DIR:/root/af_output " ..
  "  --bind $AF3_MODEL_PARAMETERS_DIR:/root/models " ..
  "  --bind $AF3_DATABASES_DIR:/root/public_databases " ..
  "  $AF3_IMAGE " ..
  "  bash -c ' " ..
  "    args=(\"$@\"); " ..
  "    for i in \"${!args[@]}\"; do " ..
  "      if [[ ${args[$i]} == --json_path=* ]]; then " ..
  "        val=${args[$i]#--json_path=}; " ..
  "        args[$i]=--json_path=/root/af_input/$(basename \"$val\"); " ..
  "      fi; " ..
  "    done; " ..
  "    python $AF3_CODE_DIR/run_alphafold.py " ..
  "      --output_dir=/root/af_output " ..
  "      --model_dir=/root/models " ..
  "      --db_dir=/root/public_databases " ..
  "      \"${args[@]}\"; " ..
  "  ' -- \"$@\"",
  -- C-shell version
  "apptainer exec --nv " ..
  "  ${XLA_PYTHON_CLIENT_PREALLOCATE:+--env XLA_PYTHON_CLIENT_PREALLOCATE=$XLA_PYTHON_CLIENT_PREALLOCATE } " ..
  "  ${TF_FORCE_UNIFIED_MEMORY:+--env TF_FORCE_UNIFIED_MEMORY=$TF_FORCE_UNIFIED_MEMORY } " ..
  "  ${XLA_CLIENT_MEM_FRACTION:+--env XLA_CLIENT_MEM_FRACTION=$XLA_CLIENT_MEM_FRACTION } " ..
  "  --bind $AF3_INPUT_DIR:/root/af_input " ..
  "  --bind $AF3_OUTPUT_DIR:/root/af_output " ..
  "  --bind $AF3_MODEL_PARAMETERS_DIR:/root/models " ..
  "  --bind $AF3_DATABASES_DIR:/root/public_databases " ..
  "  $AF3_IMAGE " ..
  "  python $AF3_CODE_DIR/run_alphafold.py " ..
  "    --output_dir=/root/af_output " ..
  "    --model_dir=/root/models " ..
  "    --db_dir=/root/public_databases " ..
  "    $*")

**What this does**

* ``set_shell_function("run_alphafold3", ...)``:
  Defines the command ``run_alphafold3`` so that when users run it (with
  ``--json_path``, environment variables for input/output/model dirs, etc.),
  the module invokes ``apptainer exec --nv`` with the correct SIF path and
  bind mounts, passing ``$@`` (Bash) or ``$*`` (C-shell).

* ``setenv("AF3_HOME", ...)`` and ``AF3_DATABASES_DIR``:
  Set the AlphaFold3 install root and shared database path; scripts or docs
  can reference these for the image path and data location.

* ``always_load("tacc-apptainer")``:
  Ensures the Apptainer environment is loaded.

* ``try_load("cuda/12.8")``:
  Loads a CUDA version compatible with the container’s GPU stack (AlphaFold3
  requires CUDA 12.6 for the Docker container); ``--nv`` then exposes the GPU.

Users load the module (e.g. ``module load alphafold3/3.0.1-ctr``), set
``AF3_INPUT_DIR``, ``AF3_OUTPUT_DIR``, and ``AF3_MODEL_PARAMETERS_DIR``, then
run ``run_alphafold3`` with ``--json_path`` pointing to their input JSON file.

Running AlphaFold3 on TACC systems
----------------------------------

Directory structure
~~~~~~~~~~~~~~~~~~~

Run from ``$SCRATCH`` (recommended). A typical project layout:

.. code-block:: text

   alphafold3_project/
   ├── input/
   │   └── example_input.json
   ├── output/
   └── slurm_jobs/

Input preparation
~~~~~~~~~~~~~~~~~~

You can provide inputs to AlphaFold3 in one of two ways:

* Single input file: Use the ``--json_path`` flag followed by the path to a single JSON file.
* Multiple input files: Use the ``--input_dir`` flag followed by the path to a directory of JSON files.

An example JSON input file is provided below: 

.. code-block:: json

   {
     "name": "UQCR11_Hsapiens",
     "sequences": [
       {
         "protein": {
           "id": "A",
           "sequence": "MVTRFLGPRYRELVKNWVPTAYTWGAVGAVGLVWATDWRLILDWVPYINGKFKKDN"
         }
       }
     ],
     "modelSeeds": [1],
     "dialect": "alphafold3",
     "version": 1
   }

Required environment variables in job scripts:

* **AF3_INPUT_DIR** — Directory containing the input ``.json`` (e.g.
  ``$SCRATCH/input``).
* **AF3_OUTPUT_DIR** — Where output will be written (e.g. ``$SCRATCH/output``).
* **AF3_MODEL_PARAMETERS_DIR** — Directory where you placed the downloaded
  AlphaFold3 model parameters (e.g. ``$WORK/af3_parameters``).

Example 1: Single protein prediction (full run on GPU)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This job runs the full AlphaFold3 pipeline (MSA + inference) on a GPU node.

.. code-block:: bash
   :caption: ``AF3_protein.slurm`` (Lonestar6)

   #!/bin/bash
   #----------------------------------------------------------------------
   #SBATCH -J AF3_protein             # Job name
   #SBATCH -o AF3_protein.o%j         # Name of stdout output file
   #SBATCH -e AF3_protein.e%j         # Name of stderr error file
   #SBATCH -p gpu-a100-small          # Queue (partition) name
   #SBATCH -N 1                       # Total # of nodes
   #SBATCH -t 01:00:00                # Run time (hh:mm:ss)
   #SBATCH -A <your-allocation>       # Allocation name
   #----------------------------------------------------------------------

   # Load required modules
   module use /scratch/tacc/apps/bio/alphafold3/modulefiles
   module load alphafold3/3.0.1-ctr

   # Set paths
   export AF3_INPUT_DIR=$SCRATCH/alphafold3_project/input/
   export AF3_OUTPUT_DIR=$SCRATCH/alphafold3_project/output/
   export AF3_MODEL_PARAMETERS_DIR=$WORK/af3_parameters

   run_alphafold3 --json_path=$AF3_INPUT_DIR/input.json

Submit with: ``sbatch AF3_protein.slurm``.

Example 2: MSA and inference separately (CPU then GPU)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Splitting the run into two stages saves GPU time: run the data pipeline (MSA
and template search) on a CPU node, then run only inference on a GPU node. See
`AlphaFold3 performance documentation
<https://github.com/google-deepmind/alphafold3/blob/main/docs/performance.md>`_.

**Step 1 — MSA only (CPU queue):**

.. code-block:: bash
   :caption: ``protein_MSA.slurm``

   #!/bin/bash
   #SBATCH -J protein_MSA
   #SBATCH -o protein_MSA.o%j
   #SBATCH -e protein_MSA.e%j
   #SBATCH -p normal                  # Normal (CPU) queue
   #SBATCH -N 1
   #SBATCH -t 01:00:00
   #SBATCH -A <your-allocation>

   module use /scratch/tacc/apps/bio/alphafold3/modulefiles
   module load alphafold3/3.0.1-ctr

   export AF3_INPUT_DIR=$SCRATCH/input/
   export AF3_OUTPUT_DIR=$SCRATCH/output/
   export AF3_MODEL_PARAMETERS_DIR=$WORK/af3_parameters

   run_alphafold3 --json_path=$AF3_INPUT_DIR/input.json --norun_inference

The output directory will contain a subdirectory named from the ``name`` field
in your ``input.json`` (e.g. ``uqcr11_hsapiens``) with a ``*_data.json`` file
for the inference step.

**Step 2 — Inference only (GPU queue):**

.. code-block:: bash
   :caption: ``protein_inference.slurm``

   #!/bin/bash
   #SBATCH -J protein_inf
   #SBATCH -o protein_inf.o%j
   #SBATCH -e protein_inf.e%j
   #SBATCH -p gpu-a100-small
   #SBATCH -N 1
   #SBATCH -t 01:00:00
   #SBATCH -A <your-allocation>

   module use /scratch/tacc/apps/bio/alphafold3/modulefiles
   module load alphafold3/3.0.1-ctr

   export AF3_INPUT_DIR=$SCRATCH/output/uqcr11_hsapiens
   export AF3_OUTPUT_DIR=$SCRATCH/output/uqcr11_hsapiens
   export AF3_MODEL_PARAMETERS_DIR=$WORK/af3_parameters

   run_alphafold3 --json_path=$AF3_INPUT_DIR/uqcr11_hsapiens_data.json --norun_data_pipeline

Important: ``AF3_INPUT_DIR`` and ``--json_path`` must point to the directory
and ``*_data.json`` file produced in Step 1.

Using multiple GPUs on a node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AlphaFold3 uses **only one GPU per run**; it does not split a single prediction
across GPUs. To use three (or more) GPUs on the same node, run **three
independent** ``run_alphafold3`` jobs in parallel, each with its own
``--json_path`` and output directory, and pin each run to a different GPU with
``CUDA_VISIBLE_DEVICES``.

Example: run 3 folds at once on a node with 3 GPUs. Use **different** input
JSON files and set ``AF3_INPUT_DIR`` and ``AF3_OUTPUT_DIR`` per run so outputs
do not overwrite each other.

.. code-block:: bash
  :caption: ``protein_3gpu.slurm`` — 3 predictions in parallel

  #!/bin/bash
  #SBATCH -J af3_3gpu
  #SBATCH -o af3_3gpu.o%j
  #SBATCH -e af3_3gpu.e%j
  #SBATCH -p gpu-a100
  #SBATCH -N 1
  #SBATCH -t 02:00:00
  #SBATCH -A <your-allocation>

  module use /scratch/tacc/apps/bio/alphafold3/modulefiles
  module load alphafold3/3.0.1-ctr

  export AF3_INPUT_DIR=$SCRATCH/input/
  export AF3_OUTPUT_DIR=$SCRATCH/output/
  export AF3_MODEL_PARAMETERS_DIR=$WORK/af3_parameters

  # Run three predictions in parallel, one per GPU
  CUDA_VISIBLE_DEVICES=0 --json_path=$AF3_INPUT_DIR/input_1.json &
  CUDA_VISIBLE_DEVICES=1 --json_path=$AF3_INPUT_DIR/input_2.json &
  CUDA_VISIBLE_DEVICES=2 --json_path=$AF3_INPUT_DIR/input_3.json &


  wait

**Notes for admins**

* **CPU and RAM**: Running three predictions on one node roughly triples CPU and
  memory use during MSA and inference. Ensure the partition’s per-node resources
  (e.g. 64 GB RAM or more for three runs) are sufficient.
* **GPU binding**: Without ``CUDA_VISIBLE_DEVICES``, all processes may use GPU 0.
  Pin each run to a specific GPU (e.g. ``0``, ``1``, ``2``) so the three runs
  use different devices.


Output 
------

AlphaFold3 generates multiple output files for each prediction. 
Here is what the output directory for one JSON input file looks like:

.. code-block:: console

  $ ls -lh
  total 459K
  drwx------ 2 kbeavers G-827556    3 Feb 19 13:53 seed-1_sample-0/
  drwx------ 2 kbeavers G-827556    3 Feb 19 13:53 seed-1_sample-1/
  drwx------ 2 kbeavers G-827556    3 Feb 19 13:53 seed-1_sample-2/
  drwx------ 2 kbeavers G-827556    3 Feb 19 13:53 seed-1_sample-3/
  drwx------ 2 kbeavers G-827556    3 Feb 19 13:53 seed-1_sample-4/
  -rw------- 1 kbeavers G-827556  13K Feb 19 13:53 TERMS_OF_USE.md
  -rw------- 1 kbeavers G-827556  31K Feb 19 13:53 UQCR11_Hsapiens_confidences.json
  -rw------- 1 kbeavers G-827556 367K Feb 19 13:52 UQCR11_Hsapiens_data.json
  -rw------- 1 kbeavers G-827556  44K Feb 19 13:53 UQCR11_Hsapiens_model.cif
  -rw------- 1 kbeavers G-827556  146 Feb 19 13:53 UQCR11_Hsapiens_ranking_scores.csv
  -rw------- 1 kbeavers G-827556  246 Feb 19 13:53 UQCR11_Hsapiens_summary_confidences.json

**Output file descriptions**

File and directory names are prefixed by the ``name`` field from your input JSON
(e.g. ``UQCR11_Hsapiens``). The most important outputs are:

* ``<name>_model.cif``: The **best-ranked predicted structure** in mmCIF format.
  This is the primary output for visualization and analysis (e.g. in PyMOL, ChimeraX,
  or for deposition).

* ``<name>_confidences.json``: Per-residue (and per-pair) confidence scores for
  the prediction. Use this to assess reliability; low-confidence regions may be
  disordered or uncertain.

* ``<name>_summary_confidences.json``: Summary confidence metrics (e.g. overall
  or chain-level scores) in JSON form.

* ``<name>_ranking_scores.csv``: Ranking of the different model samples (e.g.
  seed-1_sample-0 through seed-1_sample-4). The model with the best score corresponds
  to the structure in ``<name>_model.cif``.

* ``seed-1_sample-0/`` … ``seed-1_sample-4/``: Directories containing outputs
  for each of the five model samples (seeds). AlphaFold3 runs multiple samples and
  ranks them; the top-ranked structure is also written as ``<name>_model.cif``.
  These directories hold per-sample structures and metadata if you need them.

* ``<name>_data.json``: Intermediate data produced by the pipeline (e.g. MSA
  and feature data). Large file (~367K in the example); used when splitting
  data-pipeline and inference steps or for debugging.

* ``TERMS_OF_USE.md``: AlphaFold3 terms of use. 

**For most users**: Start with ``<name>_model.cif`` for the best predicted
structure, and use ``<name>_confidences.json`` or ``<name>_summary_confidences.json``
to check confidence. Low confidence values indicate regions to interpret with caution.

Common problems and performance
-------------------------------

* **Model parameters not found**: Ensure users have requested and downloaded
  AlphaFold3 parameters from Google and set ``AF3_MODEL_PARAMETERS_DIR`` to the
  directory where they were extracted. The module does not provide parameters.

* **GPU memory (OOM)**: AlphaFold3 is tuned for 1× A100 (80 GB) or 1× H100
  (80 GB). For larger systems or smaller GPUs (e.g. A100 40 GB), unified memory
  and/or sharding may be needed; see the `AlphaFold3 performance documentation
  <https://github.com/google-deepmind/alphafold3/blob/main/docs/performance.md>`_
  (e.g. ``XLA_PYTHON_CLIENT_PREALLOCATE=false``, ``TF_FORCE_UNIFIED_MEMORY=true``,
  ``XLA_CLIENT_MEM_FRACTION=3.2``). The TACC module can pass these through if
  set in the job environment.

* **Data pipeline slow or I/O bound**: MSA and template search are CPU- and
  disk-intensive. Running on a RAM-backed filesystem or fast SSD and
  increasing CPU cores can help. For very large-scale runs, the performance
  doc describes sharded genetic databases and parallelisation (e.g. Jackhmmer
  with multiple shards).



Additional resources
--------------------

* TACC: `AlphaFold3 at TACC <https://docs.tacc.utexas.edu/software/alphafold3/>`_
* TACC configuration: `alphafold3-config <https://github.com/kbeavers/alphafold3-config>`_
  (modulefiles and paths for Lonestar6, Frontera)
* AlphaFold3: `Google DeepMind AlphaFold3 <https://github.com/google-deepmind/alphafold3>`_
* AlphaFold3 performance: `performance.md
  <https://github.com/google-deepmind/alphafold3/blob/main/docs/performance.md>`_
* AlphaFold3 Nature paper: `Nature (2024)
  <https://www.nature.com/articles/s41586-024-07487-w>`_
* AlphaFold3 model parameters: obtain via the form linked from the TACC
  AlphaFold3 documentation; see `Google's AlphaFold 3 Model Parameters Terms of Use
  <https://docs.tacc.utexas.edu/software/alphafold3/>`_.
