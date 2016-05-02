POM Pilot
=========

Overview
--------

Generates pom.xml file with dependencies and creates Java project
directory structure.

Usage
-----

    pompilot.py [options] project-name dependency1 [dependencies]

Options
-------

    --jdk=1.8   Emit code for Java 1.8 (default)
    --jdk=1.7   Emit code for Java 1.7
    --debug     Print stack trace on error

Examples
--------

Example 1: Generate project pom.xml has JUnit dependency in test scope

    pompilot.py linux-lab1 junit:junit:4.12:scope=test

Example 2: pom.xml for Hadoop app

    pompilot.py mapreduce-lab2 \
        org.apache.hadoop:hadoop-aws:2.7.1 \
        org.apache.hadoop:hadoop-client:2.7.1 \
        com.amazonaws:aws-java-sdk-s3:1.10.30 \
        org.apache.mrunit:mrunit:1.1.0:classifier=hadoop2:scope=test \
        junit:junit:4.12:scope=test

Install
-------

    curl -LO https://raw.githubusercontent.com/asimjalis/pompilot/master/pompilot.py
    chmod 755 pompilot.py
    mv ~/pompilot.py ~/bin/.
