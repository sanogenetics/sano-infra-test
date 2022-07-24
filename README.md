![image](https://user-images.githubusercontent.com/13378850/176657886-e99a1dff-afcf-431f-a093-757cddba0d15.png)

# Sano Genetics Cloud Infrastructure Engineer Test
Thank you for taking the time to work on the Sano Genetics Cloud Infrastructure Engineer test!

⚠️ Please, **do not fork this repository**.  Instead, clone it into your own private repository called `sano-infra-test` on GitHub. Even though no coding is required for this test, we will ask you to provide your solutions in your repo's README.md file.

Ideally, you should aim to spend no longer than 3 hours on the tasks. If you can’t completely finish it, that’s not a problem - just explain what is left to do and how you would do it.

This task will involve reading and understanding the code contained inside this repository, and then using this understanding to create diagrams and future plans.

## Repository Structure

Contained inside this repository is a set of versatile scripts which use AWS CDK in the background to `setup` and `teardown` various parts of the Sano Genetics Portal infrastructure. It is used by Sano Infrastructure managers to manage Portals for different organisations across different AWS accounts, and in different AWS regions.

### /infra

Created using the recommended CDK setup, this repository contains the individual CDK stacks which create and setup resources within Cloudformation Stacks. These stacks are kept inside `/stacks`. The `app.py` file is setup to allow the CDK to setup and teardown individual stacks. `config.py` sets up logging and loads the configuration from the `infra-config` repository. `manager.py` contains the `StackManager` class which contains the core implementation details. Then, `infra.py` is a script that allows the `StackManager` to be used in custom ways based on the supplied command line arguments.

### /infra-config

This repository holds configuration for the three different production environments (prod/staging/dev), for each organisation we work with.

Each organisation's configuration is kept within a python file called `<org>.py` and split into configuration required for the infrastructure setup (`infra`), and configuration required for the server which itself is heirarchical in the same way our `zappa_settings.json` file is with a `base` config and then `env` configs that inherit from the base and override variables variables of the base.

## Example Usage (not necessary for the tasks)

Setup for a `demo` organisation:

```
python infra.py setup -o demo -s certificate  (sets up the certificate that can be used by all environments)
python infra.py setup -o demo -s org  (sets up the VPC and VPN used by all environments)
python infra.py setup -o demo -e prod -s backend  (sets up the backend resources for the production environment)
```

## Task 1

Familiarise yourself with the structure of the repository, and the CDK Stacks that are defined in the /stacks directory. You may benefit from reading through the following AWS CDK guides:

- https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
- https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html

Create a architecture diagram of the infrastructure defined in this infrastructure-as-code repository. We’d recommend using LucidChart and following [this guide](https://www.lucidchart.com/blog/how-to-build-aws-architecture-diagrams), using the AWS network diagram template.
         
Can you identify any concerns with this setup? Please link to your diagram and drop a copy of it at the bottom of the README.md file in your new `sano-infra-test` repo. Please also create a Loom video where you take us through the diagram, pointing out the concerns you found and explaining what steps could be taken to rectify them. Please also link this in the readme file.


## Task 2
Assume that Sano are in talks with a new client that uses their own database to manage their relationships with their users.

The database has a CRM with an API to interact with. As part of our Sano portal offering, some clients require that some user data is synced from the database they have attached to their running instance of the CRM with the database that resides inside the Sano portal infrastructure.

A few fields on a few tables need to be synced between the Sano DB and their DB bi-directionally, in close to real time. The solution should be able to handle a brief network connection outage between the Sano VPC and the client’s on-prem network.

Please write a document (maximum ~1 page) about the infrastructure you would set up and the code you would write to handle this requirement. Either link to this document in the README.md file or write inline at the bottom of the README.md file.

# Submitting the test

Give the GitHub user [@sano-review](https://github.com/sano-review) access to your private repository. All work related to this test should be either written or linked to in the section below.

Thank you and we hope you have fun with the test!

# Solution

This part is for you! Please drop your loom video link in here as well as anything else you'd like to add/link to.
