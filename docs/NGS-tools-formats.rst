.. NGS-tools-formats:

NSG tools and formats
=====================

Here we summarize the most common tool and standard formats for each step of NGS analysis.

NGS Data Analysis Workflow
---------------------------

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


NSG tools and formats
=====================


1.2 FastQC
~~~~~~~~~~

Run FastQC on all FASTQ files using an Apptainer container.

.. code-block:: bash

   for f in /scratch/03302/lconcia/1415_Pilot-Study-PL01/2025_10_07T15_22_11/\
   bj-dna-qc_2.0.9_25926_9126/fastq/*.fastq.gz
   do
     ls $f
     time apptainer exec /work2/03302/lconcia/sif_files/fastqc_latest.sif \
       fastqc $f
   done

1.3 Transfer FastQC results to local machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/2025_10_07T15_22_11/\
   bj-dna-qc_2.0.9_25926_9126/01_fastqc \
   /Users/lconcia/Documents/collab_TACC/bioskryb

Also transfer the MultiQC report:

.. code-block:: bash

   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/2025_10_07T15_22_11/\
   bj-dna-qc_2.0.9_25926_9126/multiqc \
   /Users/lconcia/Documents/collab_TACC/bioskryb

----

Stage 2 – Alignment with Bowtie2
----------------------------------

Paired-end reads are aligned to the maize B73 NAM 5.0 genome using Bowtie2 in ``--very-sensitive`` mode with 24 threads. The SAM output is piped directly to samtools to produce a BAM file.

2.1 Generate the alignment script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for x in /scratch/03302/lconcia/1415_Pilot-Study-PL01/2025_10_07T15_22_11/\
   bj-dna-qc_2.0.9_25926_9126/read_counts/*_R1_001.fastq.gz
   do
     echo "time apptainer exec /work2/03302/lconcia/sif_files/bowtie2_2.4.4.sif \
       bowtie2 -p 24 --very-sensitive \
       -x /work2/03302/lconcia/references/maize/miscellaneous/bowtie2_index/\
   Zm-B73-REFERENCE-NAM-5.0_genomic.with_scaffolds.bowtie_v2.4.4 \
       -1 /scratch/.../read_counts/$(basename $x _R1_001.fastq.gz)_R1_001.fastq.gz \
       -2 /scratch/.../read_counts/$(basename $x _R1_001.fastq.gz)_R2_001.fastq.gz | \
       apptainer exec /work2/03302/lconcia/sif_files/samtools_v1.9-4-deb_cv1.sif \
       samtools view -@ 8 -bS - > \
       /scratch/03302/lconcia/1415_Pilot-Study-PL01/02_bam/\
   $(basename $x _R1_001.fastq.gz).bam" ;
   done > $HOME/scripts/bowtie2.Bioskryb.7Oct2025.sh

2.2 Run alignments via pylauncher (SLURM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Launcher script** (``bowtie2.Bioskryb.7Oct2025.py``):

.. code-block:: python

   import pylauncher
   pylauncher.ClassicLauncher(
       "bowtie2.Bioskryb.7Oct2025.sh",
       cores="24",
       workdir="bowtie2.Bioskryb.7Oct2025.pylauncher_out",
       queuestate="bowtie2.Bioskryb.7Oct2025.queustate"
   )

**SLURM submission script** (``bowtie2.Bioskryb.7Oct2025.slurm``):

.. code-block:: bash

   #!/bin/bash
   #SBATCH -J bowtie2.Bioskryb.7Oct2025.slurm
   #SBATCH -o logs/bowtie2.Bioskryb.7Oct2025.%j.out
   #SBATCH -e logs/bowtie2.Bioskryb.7Oct2025.%j.err
   #SBATCH --ntasks-per-node 2
   #SBATCH -N 1
   #SBATCH -p skx
   #SBATCH -t 2:00:00
   #SBATCH -A MCB24009

   module load pylauncher
   module load tacc-apptainer

   python3 bowtie2.Bioskryb.7Oct2025.py

.. code-block:: bash

   sbatch bowtie2.Bioskryb.7Oct2025.slurm

**Result:** Overall alignment rates ranged from 98.2 %–98.9 % for single cells. Blank controls (SC05, SC06, SC07, SC08) showed <1 % alignment rates, confirming negligible contamination.

----

Stage 3 – BAM Sorting, Indexing, and Flagging QC
--------------------------------------------------

3.1 Sort and index BAM files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for f in *_L001.bam
   do
     ls $f
     time samtools sort -@8 $f > $(basename $f _L001.bam).sorted.bam
     time samtools index -@8 $(basename $f _L001.bam).sorted.bam
   done

3.2 Count total reads, properly paired reads, and supplementary alignments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for f in ../02_bam/*sorted.bam
   do
     ls $f >> all_reads.txt
     samtools view -c -@ 16 $f >> all_reads.txt

     ls $f >> unmapped+not_primary_alignment.txt
     samtools view -c -f 0x104 -@ 16 $f >> unmapped+not_primary_alignment.txt

     ls $f >> proper-pair.txt
     samtools view -c -@ 16 $f >> proper-pair.txt
     samtools view -c -f 0x2 -@ 16 $f >> proper-pair.txt

     ls $f >> supplementary_alignment.txt
     samtools view -c -f 0x800 -@ 16 $f >> supplementary_alignment.txt
   done

   # Reformat to table
   cat all_reads.txt | tr "\n" "\t" | sed -e "s/\t[^0-9]/\n /g" > all_reads.tab

**SAM flag reference:**

+----------+------------------------------------------+
| Flag     | Meaning                                  |
+==========+==========================================+
| ``0x4``  | Read unmapped                            |
+----------+------------------------------------------+
| ``0x100``| Not primary alignment                    |
+----------+------------------------------------------+
| ``0x2``  | Read mapped in proper pair               |
+----------+------------------------------------------+
| ``0x800``| Supplementary alignment                  |
+----------+------------------------------------------+

----

Stage 4 – BAM Filtering
-------------------------

High-quality uniquely-mapping reads are retained by applying a chain of samtools filters. Empty blank-control BAMs are expected after filtering.

**Filter criteria:**

- Exclude unmapped reads and non-primary alignments (``-bF 0x104``)
- Retain only properly paired reads (``-bf 0x2``)
- Exclude supplementary alignments (``-bF 0x800``)
- Require MAPQ ≥ 6 (``-q 6``)

.. code-block:: bash

   for f in *.sorted.bam
   do
     ls $f
     time samtools view -bF 0x104 -@ 8 $f | \
     samtools view -bf 0x2 -@ 8 - | \
     samtools view -bF 0x800 -@ 8 - | \
     samtools view -b -q 6 -@ 8 - > \
       /scratch/03302/lconcia/1415_Pilot-Study-PL01/03_filtered/\
   $(basename $f sorted.bam)filtered.bam \
     && \
     samtools index -@ 8 /scratch/03302/lconcia/1415_Pilot-Study-PL01/03_filtered/\
   $(basename $f sorted.bam)filtered.bam
   done

4.1 Count reads in filtered BAMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for f in ../03_filtered/*filtered.bam
   do
     ls $f >> mapq_6_or_more.txt
     samtools view -c -@ 16 $f >> mapq_6_or_more.txt
   done

   cat mapq_6_or_more.txt | tr "\n" "\t" | \
     sed -e "s/\t[^0-9]/\n /g" > mapq_6_or_more.tab

**Result:** Single cells retained ~1.3–2.2 M reads after filtering. Blank controls retained 0 reads, confirming filter effectiveness.

----

Stage 5 – BigWig Generation from Filtered BAMs
------------------------------------------------

Coverage tracks are generated at three bin sizes using deepTools ``bamCoverage``. Both RPGC-normalized and raw count bigWigs are produced.

5.1 Generate bigWig script (1 bp resolution, from sorted BAMs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for x in /scratch/03302/lconcia/1415_Pilot-Study-PL01/02_bam/*.sorted.bam
   do
     echo "time apptainer exec /work2/03302/lconcia/sif_files/\
   deeptools_3.5.4--pyhdfd78af_1.sif bamCoverage -p 48 --bam $x \
       --binSize 1 --normalizeUsing RPGC --effectiveGenomeSize 2209328549 \
       --outFileName /scratch/.../04_bigwig/$(basename $x sorted.bam)1bp.RPGC.bw \
       --outFileFormat bigwig \
     && \
     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif bamCoverage -p 48 \
       --bam $x --binSize 1 \
       --outFileName /scratch/.../04_bigwig/$(basename $x sorted.bam)1bp.bw \
       --outFileFormat bigwig" ;
   done > $HOME/scripts/bamCoverage.Bioskryb.7Oct2025.sh

5.2 Generate bigWig script (200 kb resolution, RPGC normalized)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for x in /scratch/03302/lconcia/1415_Pilot-Study-PL01/02_bam/*.sorted.bam
   do
     echo "time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $x \
       --binSize 200000 --normalizeUsing RPGC --effectiveGenomeSize 2209328549 \
       --outFileName /scratch/.../04_bigwig/$(basename $x sorted.bam)200kb.RPGC.bw \
       --outFileFormat bigwig" ;
   done > $HOME/scripts/bamCoverage.200kb.Bioskryb.8Oct2025.sh

5.3 Generate bigWig from filtered BAMs (RPGC, 200 kb)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for x in /scratch/03302/lconcia/1415_Pilot-Study-PL01/03_filtered/*.filtered.bam
   do
     echo "time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $x \
       --binSize 200000 --normalizeUsing RPGC --effectiveGenomeSize 2209328549 \
       --outFileName /scratch/.../04_bigwig/$(basename $x bam)200kb.RPGC.bw \
       --outFileFormat bigwig" ;
   done > $HOME/scripts/bamCoverage.filtered.200kb.Bioskryb.8Oct2025.sh

5.4 Submit bigWig jobs via pylauncher (SLURM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The pattern below applies to all bamCoverage jobs. Adjust script/job names accordingly.

.. code-block:: python

   # bamCoverage.filtered.200kb.Bioskryb.8Oct2025.py
   import pylauncher
   pylauncher.ClassicLauncher(
       "bamCoverage.filtered.200kb.Bioskryb.8Oct2025.sh",
       cores="48",
       workdir="bamCoverage.filtered.200kb.Bioskryb.8Oct2025.pylauncher_out",
       queuestate="bamCoverage.filtered.200kb.Bioskryb.8Oct2025.queustate"
   )

.. code-block:: bash

   #!/bin/bash
   #SBATCH -J bamCoverage.filtered.200kb.Bioskryb.8Oct2025.slurm
   #SBATCH -o logs/bamCoverage.filtered.200kb.Bioskryb.8Oct2025.%j.out
   #SBATCH -e logs/bamCoverage.filtered.200kb.Bioskryb.8Oct2025.%j.err
   #SBATCH --ntasks-per-node 1
   #SBATCH -N 1
   #SBATCH -p spr
   #SBATCH -t 0:20:00
   #SBATCH -A MCB24009

   module load pylauncher
   module load tacc-apptainer

   python3 bamCoverage.filtered.200kb.Bioskryb.8Oct2025.py

.. code-block:: bash

   sbatch bamCoverage.filtered.200kb.Bioskryb.8Oct2025.slurm

5.5 Transfer bigWig files to local machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/04_bigwig/*bw \
   /Users/lconcia/Documents/collab_TACC/bioskryb/04_bigwig

   # Transfer BAM files
   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/03_filtered \
   /Users/lconcia/Documents/collab_TACC/bioskryb/04_bigwig/20Oct2025

----

Stage 6 – Strict Uniqueness Filtering (noXS 51M) and G1-Normalized BigWigs
----------------------------------------------------------------------------

*(Update: 20 Oct 2025)*

To isolate reads that map uniquely and perfectly to the genome, an additional filtering step is applied: reads must have a 51M CIGAR string (full-length match, no soft-clipping) and must lack the ``XS`` tag (which Bowtie2 adds to reads that have a secondary alignment). This produces the cleanest possible set of reads for copy-number inference.

6.1 Filter for unique perfectly-mapping reads (noXS 51M)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``sambamba``:

.. code-block:: bash

   for f in *.filtered.bam
   do
     ls $f
     time sambamba view -h -f bam \
       -F '[XS] == null and cigar =~ /^51M$/' \
       $f -o $(basename $f bam)noXS_51M.bam
   done

Equivalent command using ``samtools`` (v1.9+):

.. code-block:: bash

   samtools view -h -b \
     -e '![XS] && rname!="*" && cigar=="51M"' \
     sample.filtered.bam -o sample.filtered.noXS_51M.bam

**Filter logic:**

- ``[XS] == null`` — no secondary alignment tag (uniquely mapping read)
- ``cigar =~ /^51M$/`` — full-length 51 bp match, no indels or soft-clips

6.2 Remove empty BAMs (blank controls)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   rm AAHJVJGM5-1415-E02_SC05_B_PL01_S313.filtered.noXS_51M.bam
   rm AAHJVJGM5-1415-F02_SC06_B_PL01_S314.filtered.noXS_51M.bam
   rm AAHJVJGM5-1415-G02_SC07_B_PL01_S315.filtered.noXS_51M.bam
   rm AAHJVJGM5-1415-H02_SC08_B_PL01_S316.filtered.noXS_51M.bam

6.3 Count reads in noXS_51M BAMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for f in *.noXS_51M.bam
   do
     ls $f >> counts.noXS_51M.txt
     samtools view -c -@ 16 $f >> counts.noXS_51M.txt
   done

   cat counts.noXS_51M.txt | tr "\n" "\t" | \
     sed -e "s/\t[^0-9]/\n /g" > counts.noXS_51M.tab

**Result:** Single cells retained ~324 k–575 k reads after noXS 51M filtering (~20–35 % of the filtered BAM reads).

6.4 Generate G1 reference bigWig
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The G1 merged BAM (``G1_all.filtered.bam``) is used as a diploid reference for normalization. Generate its RPGC-normalized coverage track:

.. code-block:: bash

   ml tacc-apptainer

   time apptainer exec /work2/03302/lconcia/sif_files/\
   deeptools_3.5.4--pyhdfd78af_1.sif bamCoverage -p 48 \
     --bam G1_all.filtered.bam \
     --binSize 200000 --normalizeUsing RPGC \
     --effectiveGenomeSize 2209328549 \
     --outFileName G1_all.filtered.200kb.RPGC.bw \
     --outFileFormat bigwig

6.5 Generate bigWigs from noXS_51M BAMs (RPGC normalized)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Three bin sizes are produced: 200 kb, 1 Mb, and 5 Mb.

.. code-block:: bash

   for f in *noXS_51M.bam
   do
     ls $f
     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 200000 --normalizeUsing RPGC \
       --effectiveGenomeSize 2209328549 \
       --outFileName ../04_bigwig/$(basename $f bam)200kb.RPGC.bw

     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 1000000 --normalizeUsing RPGC \
       --effectiveGenomeSize 2209328549 \
       --outFileName ../04_bigwig/$(basename $f bam)1Mb.RPGC.bw

     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 5000000 --normalizeUsing RPGC \
       --effectiveGenomeSize 2209328549 \
       --outFileName ../04_bigwig/$(basename $f bam)5Mb.RPGC.bw
   done

6.6 Generate bigWigs from noXS_51M BAMs (no normalization)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   for f in *noXS_51M.bam
   do
     ls $f
     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 200000 \
       --outFileName ../04_bigwig/$(basename $f bam)200kb.bw

     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 1000000 \
       --outFileName ../04_bigwig/$(basename $f bam)1Mb.bw

     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCoverage -p 48 --bam $f --outFileFormat bigwig \
       --binSize 5000000 \
       --outFileName ../04_bigwig/$(basename $f bam)5Mb.bw
   done

6.7 Compute ratio to G1 control (bamCompare)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each sample's coverage is divided by the G1 diploid coverage at 1 Mb resolution using deepTools ``bamCompare``.

.. code-block:: bash

   # On Stampede3
   for f in *noXS_51M.bam
   do
     ls $f
     time apptainer exec .../deeptools_3.5.4--pyhdfd78af_1.sif \
       bamCompare -p 48 \
       --bamfile1 $f \
       --bamfile2 G1_all.filtered.noXS_51M.bam \
       --outFileName ../04_bigwig/$(basename $f bam)1Mb.over_G1.bw \
       --outFileFormat bigwig --operation ratio --binSize 1000000
   done

   # On local machine (Stampede3 in maintenance)
   for f in *filtered.bam
   do
     ls $f
     time bamCompare -p 4 \
       --bamfile1 $f \
       --bamfile2 G1_all.filtered.bam \
       --outFileName ../04_bigwig/$(basename $f bam)1Mb.over_G1.bw \
       --outFileFormat bigwig --operation ratio --binSize 1000000
   done

6.8 Transfer final bigWig files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/04_bigwig/*.filtered.noXS_51M.*bw \
   /Users/lconcia/Documents/collab_TACC/bioskryb/04_bigwig/20Oct2025

   # Transfer G1 reference files
   scp -r lconcia@stampede3.tacc.utexas.edu:/scratch/03302/lconcia/\
   1415_Pilot-Study-PL01/03_filtered/G1_all.filtered.* \
   /Users/lconcia/Documents/collab_TACC/bioskryb/

----

Supplementary – Additional bamCoverage at 200 kb (Update: 22 Oct 2025)
------------------------------------------------------------------------

BigWigs of the filtered BAMs (not noXS_51M) at multiple bin sizes without RPGC normalization, run locally:

.. code-block:: bash

   for f in *filtered.bam
   do
     ls $f
     time bamCoverage -p 8 --bam $f --outFileFormat bigwig \
       --binSize 200000 --outFileName $(basename $f bam)200kb.bw
     time bamCoverage -p 8 --bam $f --outFileFormat bigwig \
       --binSize 1000000 --outFileName $(basename $f bam)1Mb.bw
     time bamCoverage -p 8 --bam $f --outFileFormat bigwig \
       --binSize 5000000 --outFileName $(basename $f bam)5Mb.bw
   done

----


