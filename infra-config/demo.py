infra = {
    "base": {
        "profile": "demo",
        "second_8_bits": "34",  # the second 8 bits of the Sano VPC CIDR block
        "region": "eu-west-2",
        "domain": "sanogenetics.org",
    },
    "dev": {
        "portal_subdomain": "dev.",
        "admin_subdomain": "admin.dev.",
        "media_subdomain": "media.dev.",
        "db_password": "a3XXXXXXXXXXXec",
    },
    "staging": {
        "portal_subdomain": "staging.",
        "admin_subdomain": "admin.staging.",
        "media_subdomain": "media.staging.",
        "db_password": "86XXXXXXXXXXXa5",
    },
    "prod": {
        "portal_subdomain": "",
        "admin_subdomain": "admin.",
        "media_subdomain": "media.",
        "db_password": "33XXXXXXXXXXX68",
    },
}

server_private = {
    "base": {
        "secret_salt": "$2b$12$XXXXXXXXXXX.YW.",
        "mailchimp_api_key": "37XXXXXXXXXXX16",
        "mailchimp_webhook_key": "ZZXXXXXXXXXXXqq",
        "lifebit_api_key": "AjXXXXXXXXXXXBY",
        "eurofins_api_password": "SaXXXXXXXXXXXrd",
        "picnic_health_api_key": "09XXXXXXXXXXXdd",
        "postmark_webhook_key": "1fXXXXXXXXXXXd7",
        "openexchangerates_app_id": "20XXXXXXXXXXX89",
        "easypost_api_key": "EZXXXXXXXXXXXZQ",
        "stripe_secret_key": "sk_test_oZXXXXXXXXXXX6Q",
        "tinify_api_key": "MtXXXXXXXXXXXJx",
        "genome_query_key": "rtXXXXXXXXXXX67",
        "gmaps_api_key": "AIXXXXXXXXXXXF8",
    },
    "dev": {
        "jwt_secret": "00XXXXXXXXXXXae",
        "postmark_server_token": "8aXXXXXXXXXXX48",
    },
    "staging": {
        "jwt_secret": "a2XXXXXXXXXXXfb",
        "postmark_server_token": "8aXXXXXXXXXXX48",
    },
    "prod": {
        "jwt_secret": "1aXXXXXXXXXXX33",
        "postmark_server_token": "5cXXXXXXXXXXX29",
    },
}
