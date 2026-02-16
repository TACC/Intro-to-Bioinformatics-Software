.. _data_acquisition:

Data acquisition: SRA Toolkit
=============================

This section covers downloading public sequencing data using the **SRA
(Sequence Read Archive) Toolkit** on an HPC cluster, so admins and users can
reliably stage datasets for genomics and RNA-seq workflows.

.. figure:: ./images/sra-toolkit.png
   :width: 1000px
   :align: center

   The Sequence Read Archive (SRA) `website <https://www.ncbi.nlm.nih.gov/sra>`_

What is the SRA?
----------------

The **Sequence Read Archive (SRA)** is the U.S. National Institutes of Health's
primary archive of high-throughput sequencing data, hosted at the National
Center for Biotechnology Information (NCBI). It is part of the International
Nucleotide Sequence Database Collaboration (INSDC), which also includes the
European Bioinformatics Institute (EBI) and the DNA Database of Japan (DDBJ).
Data submitted to any of these three organizations are shared among them.
`Source <https://www.ncbi.nlm.nih.gov/sra/docs/>`_.

Why it's relevant
-----------------

Researchers are often required to deposit sequencing data in the SRA as a
condition of publication. As a result, the SRA holds a large share of the
world's public sequencing data. For HPC clusters, that makes it the usual
source when users need to:

* **Reproduce published results** by downloading the same runs cited in a paper.
* **Benchmark or test** genomics and RNA-seq workflows with real, publicly
  available datasets.
* **Train or demo** tools (e.g. BWA-MEM, RNA-seq pipelines) without requiring
  local, sensitive data.

Supporting reliable, efficient downloads from the SRA—via the SRA Toolkit
described below—is therefore a common requirement for clusters that serve
bioinformatics users.

The SRA Toolkit
---------------

The **SRA Toolkit** is NCBI's set of command-line tools for downloading and
converting data from the SRA. Two commands cover most use cases:

* **prefetch** — Downloads an SRA run (e.g. ``SRR12345678``) in NCBI's native
  ``.sra`` format into a local cache. It can resume interrupted downloads and
  is the recommended first step before extracting reads.
* **fasterq-dump** — Converts cached ``.sra`` data into FASTQ files (single-
  or paired-end). It is multi-threaded and faster than the legacy ``fastq-dump``;
  it reads from the cache that ``prefetch`` fills and writes FASTQ to a
  directory you choose.

Together, **prefetch** then **fasterq-dump** is the usual workflow for getting
FASTQ data from the SRA. Run from a cache directory (e.g. ``$SCRATCH``) and use
local scratch for ``fasterq-dump`` temp files when possible. Below we outline
why this matters for HPC admins and how to run these tools on cluster systems.

Why this matters for HPC admins
--------------------------------

* **I/O and storage**: Large ``prefetch`` and ``fasterq-dump`` runs can stress
  shared filesystems. Running many concurrent downloads on login nodes can
  overload them; consider directing users to limit SRA downloads to one or two
  login nodes or use dedicated transfer nodes.
* **Network**: SRA downloads require outbound internet access, so they typically
  run on login nodes or dedicated transfer nodes. Bandwidth can be heavy;
  rate-limiting or scheduling large transfers during off-peak times may help.
* **Temporary files**: ``fasterq-dump`` writes temporary files that can be as
  large as (or larger than) the final output. Advise users to run from
  local scratch so temp files do not fill home or project space.

Best practice: where to run SRA downloads
------------------------------------------

**Running from login nodes is often necessary but not ideal.** On many clusters
only login nodes (or dedicated transfer nodes) have outbound internet access,
so SRA downloads have to run there. That does *not* make login nodes the right
place for heavy or bulk use: many users running ``prefetch``/``fasterq-dump``
at once can overload shared login nodes and hurt everyone's experience.

**Recommended approach:**

* **Prefer a dedicated transfer node** if your center provides one. Users run
  Apptainer and SRA Toolkit there; the transfer node is meant for data
  staging and can be tuned for network and I/O.
* **If users must use login nodes**, limit concurrency (e.g. one or two
  download streams per user, or use a specific login node for transfers) and
  ask users to avoid large batches. Reserve login nodes for interactive work
  and small, occasional downloads.
* **Ideal when possible:** Provide a **partition or queue with outbound
  access** so users submit a batch job that runs ``prefetch``/``fasterq-dump``
  on a compute (or transfer) node. Login nodes then stay responsive; downloads
  run in a controlled, resourced environment.

**Apptainer/Biocontainers vs. user-installed SRA Toolkit:** Using the
Biocontainers module (Apptainer) is usually better practice than having users
install SRA Toolkit themselves: you get a single, versioned, supported stack.
The "where to run" question is the same either way—both need a node with
network. Installing the toolkit themselves does not remove the need to avoid
overloading login nodes; it only changes how the binary is provided. So:
provide SRA Toolkit via Biocontainers (or a module), and pair that with a
clear policy on *where* downloads should run (transfer node or download job,
not heavy use on login nodes).

Running on TACC systems with Apptainer and Biocontainers
---------------------------------------------------------

On TACC systems, SRA Toolkit is available via the **Biocontainers** module,
which provides versioned container images that run under **Apptainer**.
First, load the required modules, then invoke the tools inside the
container.

**Load modules:**

.. code-block:: bash

   module load apptainer
   module load biocontainers

After loading, the Biocontainers module typically provides a way to run
tools by name (e.g. a wrapper or ``container run`` command). Use the
image that includes the SRA Toolkit (often named ``sra-tools`` or similar)
and run ``prefetch`` or ``fasterq-dump`` as the container entrypoint.

**Example: prefetch one accession**

Download an SRA run into a cache directory (e.g. in your ``$SCRATCH`` or
project space). Replace ``SRR_ACCESSION`` and ``/path/to/cache`` with your
accession and desired cache path.

.. code-block:: bash

   module load apptainer biocontainers

   # Cache directory: use $SCRATCH or project space, not home
   CACHE=/path/to/cache
   mkdir -p $CACHE

   # Prefetch downloads the .sra file into the cache
   prefetch --output-file $CACHE/SRR_ACCESSION.sra SRR_ACCESSION

**Example: fasterq-dump with local scratch**

Run ``fasterq-dump`` so that its temporary files go to local scratch
(``$TMPDIR`` or ``$LOCAL_SCRATCH`` on TACC). Point it at your cache and an
output directory. Use ``-e`` to set the number of threads if desired.

.. code-block:: bash

   module load apptainer biocontainers

   CACHE=/path/to/cache
   OUTDIR=/path/to/fastq/output
   ACC=SRR_ACCESSION

   mkdir -p $OUTDIR

   # Use local scratch for temp files (set by SLURM or your job script)
   cd ${TMPDIR:-/tmp}
   fasterq-dump --outdir $OUTDIR --threads 4 $CACHE/$ACC.sra

Example 1: Downloading one SRA Accession (via idev)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This walkthrough runs ``prefetch`` and ``fasterq-dump`` for a single SRA
accession (`SRR37082805 <https://www.ncbi.nlm.nih.gov/sra/?term=SRR37082805>`_)
in an interactive session on a compute node. Make sure you are working from ``$SCRATCH``
so you have enough space.

**1. Start an interactive session.** Stampede3 example: ``idev -p skx -m 30`` for 30 minutes
on the skx partition.

**2. Load modules.** The Biocontainers stack provides versioned SRA Toolkit
images. List and load a version:

.. code-block:: bash

   module load biocontainers
   module spider sra-tools          # list available versions
   module load sra-tools/ctr-3.1.1--h4304569_0

**3. Run prefetch.** This downloads the run in NCBI's ``.sra`` format into a
new directory named after the accession. Optional: use ``-v`` for verbose
output. The tool may look for Aspera (``ascp``) for faster transfer; if
not installed, it falls back to HTTPS.

.. code-block:: bash

   prefetch SRR37082805 -v

* Result: a directory ``SRR37082805/`` containing ``SRR37082805.sra``.

**4. Run fasterq-dump.** This converts the ``.sra`` file to FASTQ (raw sequencing
data + quality information).

.. admonition:: disk planning

  The final FASTQ files that users want will be ~7x the size of the ``.sra`` file.
  The ``fasterq-dump`` tool will also need temporary space of ~1.5x the size of the final
  FASTQ files during the conversion.

  Overall, the space you need for ``fasterq-dump`` is **~17x the size of the** ``.sra`` **file**.

Use ``--threads`` to match your node allocation:

.. code-block:: bash

   fasterq-dump --threads 16 SRR37082805 -v

Example output:

.. code-block:: console

    spots read      : 46,123,312
    reads read      : 92,246,624
    reads written   : 92,246,624

    $ ls -lh
    total 30G
    drwxr-xr-x 2 kbeavers G-827556 4.0K Feb 15 15:09 SRR37082805
    -rw-r--r-- 1 kbeavers G-827556  15G Feb 15 15:30 SRR37082805_1.fastq
    -rw-r--r-- 1 kbeavers G-827556  15G Feb 15 15:29 SRR37082805_2.fastq

Example 2: Batch prefetch and fasterq-dump on one node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example runs **prefetch** for all accessions in one job, then **fasterq-dump**
in a second job on one node, with at most three ``fasterq-dump`` processes running
at once. Use the same accession list for both steps. 

**1. Create an accession list.** One SRA run ID per line, e.g. ``accession_list.txt``:

.. code-block:: text

    SRR37082809
    SRR37082811
    SRR37082812
    SRR37082805
    SRR37082806
    SRR37082807
    SRR37082808
    SRR37082810
    SRR37082813

**2. Submit a prefetch job.** Run prefetch for all accessions in one job so the
``.sra`` files are on the filesystem. 

.. code-block:: bash
    :caption: ``prefetch.sbatch``

    #!/bin/bash
    #SBATCH -J prefetch_job
    #SBATCH -p skx
    #SBATCH -N 1
    #SBATCH -n 1
    #SBATCH -t 01:00:00
    #SBATCH -o logs/%x-%j.out
    #SBATCH -e logs/%x-%j.err
    #SBATCH -A <your-allocation>

    module load biocontainers
    module load sra-tools/ctr-3.1.1--h4304569_0

    prefetch --option-file accession_list.txt

**3. Submit a fasterq-dump job.** After prefetch finishes, run the script below to
convert all ``.sra`` files to FASTQ on one node.

.. code-block:: bash
   :caption: ``fasterq-dump.sbatch``

    #!/bin/bash
    #SBATCH -J fasterq-dump
    #SBATCH -p skx
    #SBATCH -N 1
    #SBATCH -n 1
    #SBATCH -t 02:00:00
    #SBATCH -o logs/%x-%j.out
    #SBATCH -e logs/%x-%j.err
    #SBATCH -A <your-allocation>

    module load biocontainers
    module load sra-tools/ctr-3.1.1--h4304569_0

    LIST=accession_list.txt
    MAX_PARALLEL=3

    echo "Node: $(hostname)  List: $LIST  Max parallel: $MAX_PARALLEL"

    # Read the list file line by line; run up to MAX_PARALLEL fasterq-dump jobs, 
    # starting the next when one finishes.
    running=0
    while read -r acc; do
        [[ -z "$acc" ]] && continue
        while (( running >= MAX_PARALLEL )); do
            wait -n
            ((running--))
        done
        fasterq-dump "$acc" --threads 12 &
        ((running++))
    done < "$LIST"
    wait

    echo "Done."

**What the script does**

* **Initialize a counter**: The variable ``running`` keeps track of how many background ``fasterq-dump`` 
  processes are currently active. 
* **Read accessions one at a time** with ``while read -r acc; do``:

   * ``read`` reads one line from the input file (``$LIST``)
   * ``acc`` stores that line (the accession ID); ``[[ -z "$acc" ]] && continue`` skips empty lines
   * ``-r`` prevents backslash interpretation
   * ``done < "$LIST"`` feeds the file into the loop so that each line becomes input

* **Enforce the parallel limit** with ``while (( running >= MAX_PARALLEL )); do``:
 
   * ``running >= MAX_PARALLEL`` checks whether we already have the maximum number of processes running
   * ``wait -n`` waits until any one background job finishes
   * ``((running--))`` decreases the counter because one job just completed 
   * The loop exits once fewer than ``MAX_PARALLEL`` jobs are running 

* **Launch a background job** with:

   * ``fasterq-dump "$acc" --threads 12 &``
   * The ``&`` symbol runs the command in the background
   * ``((running++))`` increases the counter to reflect the newly started job 

* **Wait for remaining jobs** with ``wait``:

   * After all accessions have been started, ``wait`` pauses the script until any remaining background jobs finish
   * This ensures the script does not exit early.

This script essentially behaves like a simple traffic controller for ``fasterq-dump`` jobs. It reads 
accession IDs from a file, starts up to ``MAX_PARALLEL`` converstions at once, and whenever one job finishes, 
immediately starts the next. This continues until all accessions are processed, ensuring efficient use of 
the node without oversubscribing its resources.  


Additional resources
--------------------

* **NCBI SRA**: `Sequence Read Archive <https://www.ncbi.nlm.nih.gov/sra>`_
* **SRA Toolkit**: `SRA Toolkit documentation <https://github.com/ncbi/sra-tools/wiki>`_
* **prefetch**: `prefetch documentation <https://github.com/ncbi/sra-tools/wiki/08.-prefetch-and-fasterq-dump>`_
* **TACC Stampede3**: `Stampede3 User Guide <https://docs.tacc.utexas.edu/hpc/stampede3/>`_
