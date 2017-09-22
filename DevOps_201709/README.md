ETL Pipeline Orchestration (DevOps/Data Engineer position test challenge) 
===

Data processing pipelines generally take long time to finish.
They have several steps and these steps are often run on multiple machines.
In the following text we describe an existing setup
of a simple two-step ETL pipeline with some common pitfals.

We want you to suggest and clearly describe (document)
how you would run the two steps of this pipeline
and how you would take care of the described problems.

Solve as much of the problems as you can.
Your solution does not need to be perfect or complete,
but it should show your us your level of technical skills
and the way you approach similar problems.

You can use existing software tools/libraries to complete these tasks
(unless they require us to do extensive study to understand your solution)
or you can suggest a better (more effective) pipeline setup.

If you will use existing cloud-based AWS services to accomplish the tasks,
you will earn significant bonus.


Setup
---

We have two independent linux machines (both running Ubuntu) in AWS cloud.
Let's call them *ServerA* and *ServerB*.

On *ServerA*, there is a shell script `/home/ubuntu/step1.sh`.
When run, it uses most of the available resources on the machine (RAM, CPU).

This script should be run 8-10 times per day (as often as possible,
but not too often) and it takes anywhere between one and four hours to finish.
You have no way of knowing how long the script will take to finish in advance.
It may also fail at random (exit with status code >0).

If the `step1.sh` script finishes successfully,
it writes some data into a cloud storage (S3).

On *ServerB* there is a Python script `/home/ubuntu/step2.py`.

The second script finds and reads all new the data written to S3 by `step1.sh`,
it does some processing on them and writes the results into an SQL DB.
This script should be run soon after new data from `step1.sh` are available
(as often as possible) and it also takes long time to finish.
Assume the longer time the first script took, the longer this one will take.

The second script also uses up most of the available resources on the machine.

Failures of the second script are very rare, but if they happen,
they are serious and require manual intervention.

You have SSH access to both machines with key-based authentication
and administrative rights to both of them.
You can create and use other machines and/or cloud services.


Task 1
---

Write a wrapper bash script `wrapper1.sh` which will be run on *ServerA*
in regular intervals (e.g. by cron) and which will take care of the following:

- it should run the `step1.sh` script in 2-3 hour intervals if possible
- it NEVER starts `step1.sh` script again if the previous run is still running
- it re-runs the `step1.sh` script immediately if it failed (exit code >0).

Task 2
---

Write a wrapper script "wrapper2", which will be run wherever you want
and however you want and which will take care of the following:

- it should run the script `step2.py` on *ServerB* soon (within 10 minutes)
  after the script `step1.sh` has finished and the new data are available
- it NEVER starts `step2.py` script again if the previous run is still running
- it pauses the execution of `step2.py` indefinitely if it failed once
  and notifies administrator by sending email to "etl-admin@example.com".

Deliverables: 
---

* two scripts (well commented and easy to follow)
* a document explaining what they do and how to set them up


Testing your solution 
---

If you want to test your solution in practice, you can either
setup a free-trial AWS account or simply start two VirtualBox machines
to simulate the *ServerA* and *ServerB*.

Use the scripts `step1.sh` and `step2.py` from this repository
to simulate the ETL pipeline processes.

