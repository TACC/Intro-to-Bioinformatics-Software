.. _Intro_NGS duction_to Next-generation sequencing (NGS) pipelines:

Next Generation Sequencing (NGS) pipelines
==========================================

This section shows examples of pipelines for the analyis of Next Generation Sequencing (NGS) data, together with the most used software and common data formats.


.. .. figure:: ./images/sra-toolkit.png
..   :width: 1000px
..   :align: center

..   The Sequence Read Archive (SRA) `website <https://www.ncbi.nlm.nih.gov/sra>`_

What are NGS data?
-------------------
NGS data (Next-Generation Sequencing data) are the digital output generated from biological samples using high-throughput DNA or RNA sequencing technologies.

They are obtained by extracting genetic material (DNA or RNA),  preparing sequencing libraries (fragmentation, adapter ligation, amplification),
and then running the material through a sequencing platform that reads millions to billions of nucleotide fragments in parallel. 
NGS data typically contain short or long sequence reads (strings of A, T, C, G — or U in RNA), along with associated quality scores and metadata. 

From these data, researchers can identify genetic variants, gene expression levels, mutations, structural changes, and other genomic features.

Why NGS technologies are important
----------------------------------

NGS sequencing enables rapid, high-throughput, and cost-effective analysis of DNA/RNA.
The most common applications are:

- **Oncology** and Cancer Research: Identification of somatic mutations in solid tumors and liquid biopsies to guide personalized treatments (targeted therapies).
- **Clinical Diagnostics and Hereditary Diseases**: Diagnosis of genetic disorders, including rare diseases and hereditary cancer syndromes, through whole-exome (WES) or whole-genome sequencing (WGS).
- **Infectious Disease Surveillance**: Rapid identification of pathogens (bacteria, viruses, fungi) and tracking of antimicrobial resistance and outbreaks.

- **Transcriptomics (RNA-Seq)**: Measuring gene expression levels, studying alternative splicing, and identifying fusion genes in research and diagnostics.
- **Microbiome Analysis**: Characterizing the diversity and composition of microbial communities in environmental and clinical samples.
- **Pharmacogenomics**: Understanding how an individual's genetic makeup affects their response to specific medications.


