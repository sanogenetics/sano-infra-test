import logging
from pprint import pformat

import click

from config import load_infra_config, load_server_private_config
from utils import StackManager

logger = logging.getLogger(__name__)


@click.command()
@click.argument(
    "mode",
    required=True,
    type=click.Choice(["setup", "teardown", "deploy"]),
)
@click.option(
    "-o",
    "--org",
    required=True,
    help="Name of the project",
    type=click.Choice(["flf", "demo", "bior"]),
)
@click.option(
    "-e",
    "--env",
    required=False,
    help="The environment to spin up",
    type=click.Choice(["dev", "staging", "prod"]),
    multiple=True,
)
@click.option(
    "-s",
    "--stack",
    help="The stack or set of stacks to setup/teardown ",
    required=False,
    type=click.Choice(
        [
            "certificate",
            "org",
            "server",
            "clients-no-aliases",
            "clients",
            "env-no-aliases",
            "env",
            "vpc",
            "backend",
            "portal",
            "admin",
        ]
    ),
)
def infra(mode, org, env, stack):
    # set an unused dev env for stacks that are env independent
    if env == () and stack in ["certificate", "org", "vpc"]:
        env = ("dev",)
    else:
        logger.info("Please specify an environment for this stack")

    logger.info(f"Running mode [{mode}] for stack [{stack}]")
    for en in env:
        logger.info(f"Loading config for org [{org}], env [{en}]")

        # load infra and server private config
        infra_config = load_infra_config(org, en)
        logger.info("INFRA CONFIG\n" + pformat(infra_config))
        server_private_config = load_server_private_config(org, en)
        logger.info("SERVER PRIVATE CONFIG\n" + pformat(server_private_config))

        stack_manager = StackManager(infra_config, server_private_config)

        # # testing code
        # stack_manager.test()
        # return

        if mode == "setup":
            if stack == "certificate":
                stack_manager.set_up_certificate()
            elif stack == "org":
                stack_manager.set_up_org()
            elif stack == "clients":
                stack_manager.set_up_clients(add_aliases="yes")
            elif stack == "env-no-aliases":
                stack_manager.set_up_environment()
            elif stack == "env":
                stack_manager.set_up_environment(add_aliases="yes")
            elif stack in ["vpc"]:
                stack_manager.deploy_stack(f"sano-{org}-{stack}-stack")
            elif stack in ["backend", "portal", "admin"]:
                stack_manager.deploy_stack(
                    f"sano-{org}-{en}-{stack}-stack", add_aliases="yes"
                )

        if mode == "teardown":
            if stack == "certificate":
                stack_manager.tear_down_certificate()
            elif stack == "org":
                stack_manager.tear_down_org()
            elif stack == "env":
                stack_manager.tear_down_environment()
            elif stack in ["vpc"]:
                stack_manager.destroy_stack(f"sano-{org}-{stack}-stack")
            elif stack in ["backend", "portal", "admin"]:
                stack_manager.destroy_stack(f"sano-{org}-{en}-{stack}-stack")

        if mode == "deploy":
            if stack is None:
                stack_manager.deploy_server()
                stack_manager.deploy_portal()
                stack_manager.deploy_admin()
            elif stack == "backend":
                stack_manager.deploy_server()
            elif stack == "portal":
                stack_manager.deploy_portal()
            elif stack == "admin":
                stack_manager.deploy_admin()


if __name__ == "__main__":
    infra()
