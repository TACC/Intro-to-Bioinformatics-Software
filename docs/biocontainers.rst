.. _biocontainers:

Using Biocontainers on the cluster
==================================

You have already covered Biocontainers (and Singularity/Apptainer) in prior
training. This section briefly ties that into the workflows in this
documentation.

How we use containers here
--------------------------

* In each workflow below, commands assume you can run tools from a
  **Biocontainer** image (e.g. from `quay.io/biocontainers` or your local
  registry).
* We use **Singularity/Apptainer** as the runtime; substitute your cluster’s
  command (e.g. ``singularity run`` or ``apptainer run``) as needed.
* Images are referenced by tag so that runs are **reproducible** and
  consistent across nodes.

What you need on the cluster
----------------------------

* Singularity or Apptainer installed and available on compute nodes.
* Either pull from a public registry (if allowed) or a **local mirror** of
  Biocontainers so jobs don’t all hit the same external service.
* (Optional) A module or wrapper so users get a consistent image path and
  version for each tool.

In the following pages (data acquisition, genomics, RNA-seq, etc.), we will
show example invocations using a container for each tool. If your site uses
environment modules or custom wrappers, you can adapt the examples to call
those instead while keeping the same workflow logic and resource requests.
