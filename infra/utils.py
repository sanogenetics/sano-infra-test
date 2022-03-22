import logging
import subprocess
from time import sleep

import boto3

logger = logging.getLogger(__name__)


# runs a command in the shell while retaining logs
def run(command, **kwargs):
    output = ""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        **kwargs,
    )
    while process.poll() is None:
        line = process.stdout.readline().decode()
        output += line
        while line:
            logger.log(logging.INFO, line.strip())
            line = process.stdout.readline().decode()
            output += line

    return output


class StackManager:
    def __init__(self, infra_config, server_private_config):
        self.infra_config = infra_config
        self.server_private_config = server_private_config
        self.org = infra_config["org"]
        self.env = infra_config["env"]
        self.aws_profile = infra_config["profile"]
        self.portal_dir = infra_config["portal_dir"]
        self.admin_dir = infra_config["admin_dir"]
        self.domain = infra_config["domain"]
        self.SOE = f"sano-{self.org}-{self.env}"
        self.lambda_function_name = f"sano-server-{self.env}-{self.org}"

        # set boto3 clients
        boto3.setup_default_session(profile_name=self.aws_profile)
        self.lambda_client = boto3.client("lambda")
        self.ec2_client = boto3.client("ec2")
        self.rds_client = boto3.client("rds")
        self.cloudfront_client = boto3.client("cloudfront")
        self.virginia_lambda_client = boto3.client("lambda", region_name="us-east-1")

        # get AWS resources
        self.api_gateway_url = self.get_api_gateway_url()
        self.certificate_arn = self.get_certificate_arn()
        self.redirect_lambda_arn = self.get_redirect_lambda_arn()
        self.cdk_context = self.get_cdk_context_string()

    # function to experiment
    def test(self):
        print(self.api_gateway_url)

    def get_redirect_lambda_arn(self):
        self.virginia_lambda_client.list_versions_by_function
        redirect_lambda_arn = None
        for function in self.virginia_lambda_client.list_functions()["Functions"]:
            if function["FunctionName"] == "s3-302-redirect":
                versions = self.virginia_lambda_client.list_versions_by_function(
                    FunctionName="s3-302-redirect",
                )["Versions"]
                for version in versions:
                    redirect_lambda_arn = version["FunctionArn"]

        print(redirect_lambda_arn)
        return redirect_lambda_arn

    # get the api gateway url of the zappa setup
    def get_api_gateway_url(self):
        api_gateway_client = boto3.client("apigateway")
        apis = api_gateway_client.get_rest_apis()["items"]
        api_id = None
        for api in apis:
            if api["name"] == self.lambda_function_name:
                api_id = api["id"]
        return f"{api_id}.execute-api.{self.infra_config['region']}.amazonaws.com"

    # get the ARN of the certificate for the domain of the infra that's being set up
    def get_certificate_arn(self):
        # certificates must live in N. Virginia
        acm_client = boto3.client("acm", region_name="us-east-1")
        certificates = acm_client.list_certificates()["CertificateSummaryList"]
        certificate_arn = None
        for certificate in certificates:
            if certificate["DomainName"] == self.domain:
                certificate_arn = certificate["CertificateArn"]
        return certificate_arn

    # get backend subnet IDs
    def get_subnet_ids(self):
        subnet_ids = []
        subnets = self.ec2_client.describe_subnets()["Subnets"]
        for subnet in subnets:
            tags = subnet.get("Tags")
            if tags is not None:
                for tag in tags:
                    if tag.get("Key") == "aws:cloudformation:logical-id" and tag.get(
                        "Value"
                    ).startswith(f"sano{self.org}{self.env}dbsubnet"):
                        subnet_ids.append(subnet["SubnetId"])
        return subnet_ids

    # get backend security group ID
    def get_security_group_id(self):
        response = self.ec2_client.describe_security_groups(
            Filters=[
                dict(Name="group-name", Values=[f"{self.SOE}-lambda-security-group"])
            ]
        )
        return response["SecurityGroups"][0]["GroupId"]

    # get backend connection string
    def get_connection_string(self):
        instances = self.rds_client.describe_db_instances(
            DBInstanceIdentifier=f"{self.SOE}-db"
        )
        db_host = instances.get("DBInstances")[0].get("Endpoint").get("Address")
        return f"postgresql://{self.infra_config['db_username']}:{self.infra_config['db_password']}@{db_host}:5432/{self.env}"

    # gets a context string to be passed through to the CDK to deploy the stacks
    def get_cdk_context_string(self):
        variables = [
            "org",
            "env",
            "region",
            "second_8_bits",
            "db_username",
            "db_password",
            "domain",
            "portal_subdomain",
            "admin_subdomain",
            "media_subdomain",
            "api_gateway_url",
            "certificate_arn",
            "redirect_lambda_arn",
        ]
        self.infra_config["api_gateway_url"] = self.api_gateway_url
        self.infra_config["certificate_arn"] = self.certificate_arn
        self.infra_config["redirect_lambda_arn"] = self.redirect_lambda_arn
        context = dict(((k, self.infra_config[k]) for k in variables))
        return " ".join([f"-c {k}={v}" for (k, v) in context.items()])

    # runs zappa with specified action
    def run_zappa(self, action):
        command = f"source venv/bin/activate && zappa {action} {self.env}_{self.org}"
        if action == "undeploy":
            command = command + " --yes"
        run(command, cwd=self.infra_config["server_dir"])

    # deploy a stack
    def deploy_stack(self, stack, add_aliases="no"):
        logger.info(f"Deploying {stack}")
        run(
            f"cdk deploy {stack} --profile {self.aws_profile} {self.cdk_context} -c add_aliases={add_aliases} --require-approval never"
        )

    # destroy a stack
    def destroy_stack(self, stack):
        logger.info(f"Destroying {stack}")
        run(
            f"cdk destroy {stack} --profile {self.aws_profile} {self.cdk_context} --force"
        )

    def link_zappa_and_set_env_vars(self, setup=False):
        variables = self.server_private_config
        if setup:
            variables["migrate"] = "True"
        variables["base_url"] = self.infra_config["portal_url"]
        variables["admin_url"] = self.infra_config["admin_url"]
        variables["connection_string"] = self.get_connection_string()
        self.lambda_client.update_function_configuration(
            FunctionName=self.lambda_function_name,
            Environment={"Variables": variables},
            VpcConfig={
                "SubnetIds": self.get_subnet_ids(),
                "SecurityGroupIds": [
                    self.get_security_group_id(),
                ],
            },
        )

    def clear_s3_bucket(self, name):
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(name)
        try:
            bucket.object_versions.all().delete()
        except Exception:
            pass

    def unlink_zappa(self):
        try:
            self.lambda_client.update_function_configuration(
                FunctionName=self.lambda_function_name,
                Environment={},
                VpcConfig={
                    "SubnetIds": [],
                    "SecurityGroupIds": [],
                },
            )
        except Exception:
            logger.warning(f"{self.lambda_function_name} lambda function not found.")

    def deploy_portal(self, invalidate_cache=True):
        run(
            "npm install",
            cwd=self.portal_dir,
        )
        output = run(
            f"unset HOST && npm run build-{self.org}-{self.env}",
            cwd=self.portal_dir,
        )
        if "ERROR" in output:
            return
        run(
            f"aws s3 rm s3://{self.SOE}-portal --recursive --profile {self.aws_profile}",
            cwd=self.portal_dir,
        )
        run(
            f'aws s3 sync --cache-control "max-age=3600" dist/{self.org}/{self.env}/ s3://{self.SOE}-portal --profile {self.aws_profile}',
            cwd=self.portal_dir,
        )

        if invalidate_cache:
            distribution_id = ""
            for distribution in self.cloudfront_client.list_distributions()[
                "DistributionList"
            ]["Items"]:
                alias = (
                    distribution["Aliases"]["Items"][0]
                    if "Items" in distribution["Aliases"]
                    else None
                )
                if f"{self.infra_config['portal_subdomain']}{self.domain}" == alias:
                    distribution_id = distribution["Id"]
            run(
                f'aws cloudfront create-invalidation --distribution-id {distribution_id} --paths "/*" --profile {self.aws_profile}',
                cwd=self.portal_dir,
            )

    def deploy_admin(self, invalidate_cache=True):
        run(
            "npm install",
            cwd=self.admin_dir,
        )
        output = run(
            f"npm run build-{self.org}-{self.env}",
            cwd=self.admin_dir,
        )
        if "ERROR" in output:
            return
        run(
            f"aws s3 rm s3://{self.SOE}-admin --recursive --profile {self.aws_profile}",
            cwd=self.admin_dir,
        )
        run(
            f'aws s3 sync --cache-control "max-age=3600" dist/{self.org}/{self.env} s3://{self.SOE}-admin --profile {self.aws_profile}',
            cwd=self.admin_dir,
        )

        if invalidate_cache:
            distribution_id = ""
            for distribution in self.cloudfront_client.list_distributions()[
                "DistributionList"
            ]["Items"]:
                alias = (
                    distribution["Aliases"]["Items"][0]
                    if "Items" in distribution["Aliases"]
                    else None
                )
                if f"{self.infra_config['admin_subdomain']}{self.domain}" == alias:
                    distribution_id = distribution["Id"]
            run(
                f'aws cloudfront create-invalidation --distribution-id {distribution_id} --paths "/*" --profile {self.aws_profile}',
                cwd=self.admin_dir,
            )

    def deploy_server_no_migration(self):
        logger.info("Linking ZAPPA stack to BACKEND stack (auto migration disabled)")
        self.link_zappa_and_set_env_vars()
        logger.info("Updating ZAPPA stack")
        self.run_zappa("update")

    def deploy_server(self):
        logger.info("Linking ZAPPA stack to BACKEND stack (auto migration enabled)")
        self.link_zappa_and_set_env_vars(setup=True)
        logger.info("Updating ZAPPA stack")
        self.run_zappa("update")

    # for this to complete the certificate must receive validation through an email to the domain controller
    def set_up_certificate(self):
        logger.info(f"Deploying {self.domain} CERTIFICATE stack")
        self.deploy_stack(
            f"sano-{self.org}-certificate-stack-{self.domain.replace('.', '-')}"
        )

    def tear_down_certificate(self):
        logger.info(f"Destroying {self.domain} CERTIFICATE stack")
        self.destroy_stack(
            f"sano-{self.org}-certificate-stack-{self.domain.replace('.', '-')}"
        )

    def set_up_org(self):
        # Deploy VPC stack
        self.deploy_stack(f"sano-{self.org}-vpc-stack")
        # Deploy VPN stack
        self.deploy_stack(f"sano-{self.org}-vpn-stack")

    def tear_down_org(self):
        # Destroy VPN stack
        self.destroy_stack(f"sano-{self.org}-vpn-stack")
        # Destroy VPC stack
        self.destroy_stack(f"sano-{self.org}-vpc-stack")

    def set_up_server(self):
        # Deploy BACKEND stack
        self.deploy_stack(f"{self.SOE}-backend-stack")

        logger.info("Deploying ZAPPA stack")
        self.run_zappa("deploy")
        logger.info("Waiting for ZAPPA stack to finish deploying")
        sleep(120)
        # fetch the API gateway again (in case it was None on initial fetch)
        self.api_gateway_url = self.get_api_gateway_url()
        logger.info("Linking ZAPPA stack to BACKEND stack (auto migration enabled)")
        self.link_zappa_and_set_env_vars(setup=True)
        logger.info("Waiting for ZAPPA stack to finish being linked")
        sleep(120)
        logger.info("Updating ZAPPA stack")
        self.run_zappa("update")
        logger.info("Waiting for ZAPPA stack to finish updating")
        sleep(120)
        self.deploy_server()

    def set_up_clients(self, add_aliases="no"):
        # Deploy PORTAL stack
        self.deploy_stack(f"{self.SOE}-portal-stack", add_aliases)
        self.deploy_portal(invalidate_cache=(add_aliases == "yes"))

        # Deploy ADMIN stack
        self.deploy_stack(f"{self.SOE}-admin-stack", add_aliases)
        self.deploy_admin(invalidate_cache=(add_aliases == "yes"))

        # Deploy MEDIA stack
        self.deploy_stack(f"{self.SOE}-media-stack", add_aliases)

    def set_up_environment(self, add_aliases="no"):
        self.set_up_server()
        self.set_up_clients(add_aliases)

    def tear_down_environment(self):
        # Destroy MEDIA stack
        self.clear_s3_bucket(f"{self.SOE}-media-uploads")
        self.destroy_stack(f"{self.SOE}-media-stack")

        # Destroy ADMIN stack
        self.clear_s3_bucket(f"{self.SOE}-admin")
        self.destroy_stack(f"{self.SOE}-admin-stack")

        # Destroy PORTAL stack
        self.clear_s3_bucket(f"{self.SOE}-portal")
        self.destroy_stack(f"{self.SOE}-portal-stack")

        # Destroy ZAPPA and BACKEND stacks
        logger.info("Unlinking ZAPPA stack from backend")
        self.unlink_zappa()
        logger.info("Destroying ZAPPA stack")
        self.run_zappa("undeploy")
        # the lambda security groups needs the lambda function to be deleted before it can be
        logger.info("Waiting for ZAPPA stack to undeploy")
        sleep(120)

        self.clear_s3_bucket(f"{self.SOE}-uploads")
        self.destroy_stack(f"{self.SOE}-backend-stack")
