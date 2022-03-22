import logging
import os
import sys
from logging import handlers

import coloredlogs

# logging setup
format_string = (
    "%(levelname)s: %(asctime)s %(funcName)s() %(name)s:%(lineno)s %(message)s"
)
logging.basicConfig(
    level=logging.INFO,
    format=format_string,
    handlers=[
        logging.StreamHandler(sys.stdout),
        handlers.RotatingFileHandler(
            "logs/infra.log", maxBytes=(1048576 * 5), backupCount=7
        ),
    ],
)
coloredlogs.install(
    level="INFO",
    fmt=format_string,
)


def load_infra_config(org, env):
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "infra-config"))
    shared_infra = getattr(__import__("shared", fromlist=["infra"]), "infra")
    org_infra = getattr(__import__(org, fromlist=["infra"]), "infra")
    infra_config = shared_infra["base"]
    infra_config.update(shared_infra[env])
    infra_config.update(org_infra["base"])
    infra_config.update(org_infra[env])
    infra_config["org"] = org
    infra_config["env"] = env
    infra_config[
        "portal_url"
    ] = f"https://{infra_config['portal_subdomain']}{infra_config['domain']}"
    infra_config[
        "admin_url"
    ] = f"https://{infra_config['admin_subdomain']}{infra_config['domain']}"
    infra_config["db_username"] = env
    return infra_config


def load_server_private_config(org, env):
    # form the config required for the server
    shared_server_private = getattr(
        __import__("shared", fromlist=["server_private"]), "server_private"
    )
    org_server_private = getattr(
        __import__(org, fromlist=["server_private"]), "server_private"
    )
    server_private_config = {"env": env, "org": org}
    server_private_config.update(shared_server_private["base"])
    server_private_config.update(shared_server_private[env])
    server_private_config.update(org_server_private["base"])
    server_private_config.update(org_server_private[env])
    return server_private_config
