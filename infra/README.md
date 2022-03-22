# Sano Infrastructure

A versatile script that uses AWS CDK in the background to `setup` or `teardown` various parts
of the Sano Genetics portal infrastructure. Used by Sano infrastructure managers to manage portals
for different organisations across different AWS account and in different AWS regions.

## Installation

Create a python virtual environment and install the required libraries

```bash
  virtualenv -p python3 venv
  source venv/bin/activate
  pip install -r requirements.txt
```

## Repository Structure

### infra-config

A repository holding configuration for the different production environments (prod/staging/dev currently), for each organisation. This repository lives on the deploy server only and does not have a remote for security reasons.

Each organisation's configuration is kept within a python file called `<org>.py` and split into configuration required for the infrastructure setup (`infra`), and configuration required for the server which itself is heirarchical in the same way our `zappa_settings.json` file is with a `base` config and then `env` configs that inherit from the base and override variables variables of the base.

### infra

Created using the recommended CDK setup, this repository contains the individual CDK stacks which create and setup resources within Cloudformation stacks. These stacks are kept inside `/stacks`. An `app.py` file is setup to allow the CDK to run and setup / teardown individual stacks. `config.py` sets up logging and loads the configuration from the `infra-config` repository which should be kept on the same folder level as this repository. `manager.py` contains the `StackManager` class which is where the main implementation lies. Then, `infra.py` is a script that allows the `StackManager` to be used in various ways based on supplied command line arguments.

## AWS Account Setup

For each portal that Sano controls, a new AWS account is created so that the new portal is separate from others.
From there, we can either add the portal client staff as admins to this AWS account, or transfer control of the entire AWS account to them and keep a few admin user accounts ourselves for management of the portal.

The process to follow to set up a new account is currently as follows:

- Sign up new account under daniel+<org>@sanogenetics.com
- Create a secure password and add it to the admin vault in 1Password.
- Add Will's Sano credit card information to the account
- In the IAM console, add new user `daniel` with programmatic access only and attach the AWS built in AdministratorAccessGroup group to this user - while you have the access keys, do the next step
- Add the access keys that are shown at the end of the above step to `~/.aws/credentials` like:

```
    [<org>]
    aws_access_key_id = AKXXXXXXXXXXXXX5W
    aws_secret_access_key = CnXXXXXXXXXXXXXXul
```

- Add a new profile to `~/.aws/config` like:

```
    [profile <org>]
    region=<region>
```

## Org Infrastructure Setup

Some of the infrastructure stacks are environment independent. These are setup first, and then the environment
dependant stacks can be set up afterwards. This process is called `Org Infrastructure Setup` and includes the setup of the Certificate stack, the VPC stack, and the VPN stack.

The following instructions setup the base org infrastructure on which the environment infrastructure can be placed into:

- Duplicate a config file in the infra-config repository and set second_8_bits to be unique for this AWS account / region combo.
- Perform the following command line steps to generate and upload VPN client and server keys. The last two steps need variable replacements of <org> and <region>
  ```bash
  git clone https://github.com/OpenVPN/easy-rsa.git
  cd easy-rsa/easyrsa3
  ./easyrsa init-pki
  ./easyrsa build-ca nopass
  ./easyrsa build-server-full server nopass
  ./easyrsa init-pki
  ./easyrsa build-ca nopass
  ./easyrsa build-server-full server nopass
  ./easyrsa build-client-full client1.domain.tld nopass
  mkdir ~/custom_folder/
  cp pki/ca.crt ~/custom_folder/
  cp pki/issued/server.crt ~/custom_folder/
  cp pki/private/server.key ~/custom_folder/
  cp pki/issued/client1.domain.tld.crt ~/custom_folder
  cp pki/private/client1.domain.tld.key ~/custom_folder/
  cd ~/custom_folder/
  aws acm import-certificate --certificate fileb://server.crt --private-key fileb://server.key --certificate-chain fileb://ca.crt --profile <org> --region <region>
  aws acm import-certificate --certificate fileb://client1.domain.tld.crt --private-key fileb://client1.domain.tld.key --certificate-chain fileb://ca.crt --profile <org> --region <region>
  ```
- Copy the ARNs given back to your into the right place in the vpn_stack.py file in the infra repo
- TBD

DOCUMENTATION UNFINISHED
