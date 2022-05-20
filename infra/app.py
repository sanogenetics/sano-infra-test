#!/usr/bin/env python3
import logging

from aws_cdk import core as cdk

from stacks.admin_stack import AdminStack
from stacks.backend_stack import BackendStack
from stacks.certificate_stack import CertificateStack
from stacks.portal_stack import PortalStack
from stacks.vpc_stack import VpcStack

logger = logging.getLogger(__name__)

app = cdk.App()
org = app.node.try_get_context("org")
env = app.node.try_get_context("env")
region = app.node.try_get_context("region")
second_8_bits = app.node.try_get_context("second_8_bits")
db_username = app.node.try_get_context("db_username")
db_password = app.node.try_get_context("db_password")
domain = app.node.try_get_context("domain")
domains = [domain, f"*.{domain}", f"*.dev.{domain}", f"*.staging.{domain}"]
portal_subdomain = app.node.try_get_context("portal_subdomain")
admin_subdomain = app.node.try_get_context("admin_subdomain")
api_gateway_url = app.node.try_get_context("api_gateway_url")
certificate_arn = app.node.try_get_context("certificate_arn")
redirect_lambda_arn = app.node.try_get_context("redirect_lambda_arn")
add_aliases = app.node.try_get_context("add_aliases")

SOE = f"sano-{org}-{env}"

certificate_stack = CertificateStack(
    app,
    f"sano-{org}-certificate-stack-{domain.replace('.', '-')}",
    org=org,
    domains=domains,
    env=cdk.Environment(region="us-east-1"),
)

vpc_stack = VpcStack(
    app,
    f"sano-{org}-vpc-stack",
    org=org,
    region=region,
    second_8_bits=second_8_bits,
    env=cdk.Environment(region=region),
)

backend_stack = BackendStack(
    app,
    f"{SOE}-backend-stack",
    org=org,
    envir=env,
    region=region,
    vpc=vpc_stack.vpc,
    nat_gateway=vpc_stack.nat_gateway,
    second_8_bits=second_8_bits,
    db_username=db_username,
    db_password=db_password,
    env=cdk.Environment(region=region),
)
backend_stack.add_dependency(vpc_stack)
# backend_stack.add_dependency(certificate_stack)  # disable when you created the certificate manually

portal_stack = PortalStack(
    app,
    f"{SOE}-portal-stack",
    org=org,
    envir=env,
    region=region,
    domain=domain,
    portal_subdomain=portal_subdomain,
    api_gateway_url=api_gateway_url,
    certificate_arn=certificate_arn,
    redirect_lambda_arn=redirect_lambda_arn,
    add_aliases=add_aliases,
    env=cdk.Environment(region=region),
)

admin_stack = AdminStack(
    app,
    f"{SOE}-admin-stack",
    org=org,
    envir=env,
    region=region,
    domain=domain,
    admin_subdomain=admin_subdomain,
    api_gateway_url=api_gateway_url,
    certificate_arn=certificate_arn,
    add_aliases=add_aliases,
    env=cdk.Environment(region=region),
)

app.synth()
