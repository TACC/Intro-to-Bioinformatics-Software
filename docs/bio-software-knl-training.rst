.. _bioinformatics_software_knl_training:

Bioinformatics Software on KNL Nodes
====================================

The goal of this module is to show how bioinformatics workloads 
behave on a HPC cluster (CPU threads, memory bandwidth, filesystem I/O,
dependency management, and reproducibility) and how to run representative 
tools efficiently on many-core nodes.

Learning Objectives 
--------------------

By the end of this module, participants should be able to:

* Identify whether a bioinformatics tools is **CPU-bound**, **memory bound**, or **I/O bound**
* Correctly request resources and set thread counts for multi-threaded tools
* Use **Biocontainers/Singularity/Apptainer** to run common genomics/RNA-seq tools reproducibly
* Launch parameter sweeps and per-sample processing with **SLURM job arrays**
* Diagnose common failure modes: underspecified memory, filesystem bottlenecks,
  oversubscription, and mismatched ``cpus-per-task`` vs tool threads

Assumptions / prerequisites
---------------------------

* SLURM is used as the scheduler (examples assume SLURM).
* Participants have access to a KNL partition (or similar many-core nodes).
* Biocontainers (or a local container registry) are available.
* Participants are comfortable with basic shell usage.
