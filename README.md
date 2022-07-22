![image](https://user-images.githubusercontent.com/13378850/176657886-e99a1dff-afcf-431f-a093-757cddba0d15.png)

# Sano Genetics Cloud Infrastructure Engineer Test
Thank you for taking the time to work on the Sano Genetics Cloud Infrastructure Engineer test!

⚠️ Please, **do not fork this repository**.

Ideally, you should aim to spend no longer than 3 hours on the tasks. If you can’t completely finish it, that’s not a problem - just explain what is left to do and how you would do it.

This task will involve reading and understanding the code contained inside this repository, and then using this understanding to create diagrams and future plans.

## Repository Structure

Contained inside this repository is a set of versatile scripts which use AWS CDK in the background to `setup` and `teardown` various parts
of the Sano Genetics Portal infrastructure. It is used by Sano Unfrastructure managers to manage Portals
for different organisations across different AWS accounts, and in different AWS regions.

### /infra

Created using the recommended CDK setup, this repository contains the individual CDK stacks which create and setup resources within Cloudformation Stacks. These stacks are kept inside `/stacks`. The `app.py` file is setup to allow the CDK to setup and teardown individual stacks. `config.py` sets up logging and loads the configuration from the `infra-config` repository which should be kept on the same folder level as this repository. `manager.py` contains the `StackManager` class which contains the core implementation details. Then, `infra.py` is a script that allows the `StackManager` to be used in custom ways based on the supplied command line arguments.

### /infra-config

This repository holds configuration for the different production environments (prod/staging/dev), for each organisation we work with.

Each organisation's configuration is kept within a python file called `<org>.py` and split into configuration required for the infrastructure setup (`infra`), and configuration required for the server which itself is heirarchical in the same way our `zappa_settings.json` file is with a `base` config and then `env` configs that inherit from the base and override variables variables of the base.

## Usage (not necessary for the tasks)

Setup for a `demo` organisation:

```
python infra.py setup -o demo -s certificate
```

## Task 1

Familiarise yourself with the structure of the repository, and the CDK Stacks that are defined in the /stacks directory. You may benefit from reading through the following AWS CDK guides:
https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html

Create a network architecture diagram of the infrastructure defined in this infrastructure-as-code repository. We’d recommend using LucidChart and following this guide, using the ​​AWS network diagram template.
         
Can you identify any concerns with this setup? Please send us your diagram and create a Loom video where you take us through the diagram, pointing out the concerns you found and explaining what steps could be taken to rectify them.

## Task 2
Assume that Sano are in talks with a new client that uses their own database to manage their relationships with their users.

The database has a CRM with an API to interact with. As part of our Sano portal offering, the client requires that some user data is synced from the database they have attached to their running instance of the CRM with the database that resides inside the Sano infrastructure.

A few fields on a few tables need to be synced between the Sano DB and their DB bi-directionally, in close to real time. The solution should be able to handle a brief network connection outage between the Sano VPC and the client’s on-prem network.

Please write a document (maximum 1 page) about the infrastructure you would set up and the code you would write to handle this requirement.
