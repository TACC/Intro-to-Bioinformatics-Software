.. NGS-tools-formats:

NSG tools and formats
=====================

The table below summarizes tools used in the first steps in a typical NGS data workflow.

+------------------------+-------------------+-------------------+-------------------+---------------------------+
| **Step**               | **Tool**          | **Input Formats** | **Output Formats**| **Multithreading**        |
+========================+===================+===================+===================+===========================+
| Quality Control        | FASTQC            | FASTQ             | HTML, ZIP         | No                        |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Quality Control        | FASTP             | FASTQ             | FASTQ, JSON, HTML | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Adapter Trimming       | Trimmomatic       | FASTQ             | FASTQ             | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Adapter Trimming       | Cutadapt          | FASTQ             | FASTQ             | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Alignment to Genome    | Bowtie2           | FASTQ             | SAM               | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Alignment to Genome    | STAR              | FASTQ             | SAM/BAM           | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Alignment to Genome    | BWA               | FASTQ             | SAM               | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Post-processing        | samtools sort     | SAM/BAM           | BAM               | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Post-processing        | samtools index    | BAM               | BAI               | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Post-processing        | samtools filter   | BAM               | BAM               | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Downstream Analysis    | HTSeq             | BAM, GTF          | TXT (counts)      | Limited                   |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Downstream Analysis    | deepTools         | BAM, BED, BigWig  | BigWig, TXT       | Yes                       |
+------------------------+-------------------+-------------------+-------------------+---------------------------+
| Downstream Analysis    | BEDTools          | BAM, BED, GTF     | BED, TXT          | Limited                   |
+------------------------+-------------------+-------------------+-------------------+---------------------------+

When multithreading is available, the number of cores can be selected with a specific option (-p, -t --threads, etc ...) 
For single-threading tools, multiple parallel processes can be launched with PyLauncher or SLURM arrays.


Examples
==================  
