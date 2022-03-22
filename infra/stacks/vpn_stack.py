from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk

# NB: manual work required here for now - follow these instructions verbatim and import both certificates into your region:
# https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual
# copy custom_folder to somewhere structured locally
# run these to upload them
# aws acm import-certificate --certificate fileb://server.crt --private-key fileb://server.key --certificate-chain fileb://ca.crt --profile XXX --region XXX
# aws acm import-certificate --certificate fileb://client1.domain.tld.crt --private-key fileb://client1.domain.tld.key --certificate-chain fileb://ca.crt --profile XXX --region XXX

# Note their arns and replace the arn values below
# Don't forget point 5 in step 6 here when you set up the client config file for VPN connection:
# https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
server_certificate_arn = (
    "arn:aws:acm:eu-west-2:06XXXXXXXXXXX64:certificate/abXXXXXXXXXXX8c"
)
client_certificate_arn = (
    "arn:aws:acm:eu-west-2:06XXXXXXXXXXX64:certificate/84XXXXXXXXXXX5a"
)


class VpnStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        org,
        region,
        vpc: ec2.Vpc,
        internet_gateway: ec2.CfnInternetGateway,
        second_8_bits,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        id = f"sano-{org}-vpn-security-group"
        vpn_security_group = ec2.CfnSecurityGroup(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            group_description=id,
            group_name=id,
            vpc_id=vpc.ref,
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    source_security_group_id=vpc.attr_default_security_group,
                    ip_protocol="-1",
                ),
            ],
            security_group_egress=[
                ec2.CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ip="0.0.0.0/0",
                )
            ],
        )

        id = f"sano-{org}-vpn-subnet"
        client_vpn_subnet = ec2.PrivateSubnet(
            self,
            id,
            availability_zone=f"{region}a",
            cidr_block=f"172.{second_8_bits}.48.0/24",
            vpc_id=vpc.ref,
            map_public_ip_on_launch=False,
        )

        id = f"sano-{org}-vpn-internet-gateway-route"
        ec2.CfnRoute(
            self,
            id,
            route_table_id=client_vpn_subnet.route_table.route_table_id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.ref,
        )

        id = f"sano-{org}-client-vpn-endpoint"
        client_vpn_endpoint = ec2.CfnClientVpnEndpoint(
            self,
            id,
            tag_specifications=[
                ec2.CfnClientVpnEndpoint.TagSpecificationProperty(
                    tags=[cdk.CfnTag(key="Name", value=id)],
                    resource_type="client-vpn-endpoint",
                )
            ],
            description="client-vpn-endpoint",
            client_cidr_block="192.168.0.0/16",
            dns_servers=[f"172.{second_8_bits}.0.2"],
            transport_protocol="udp",
            server_certificate_arn=server_certificate_arn,
            authentication_options=[
                ec2.CfnClientVpnEndpoint.ClientAuthenticationRequestProperty(
                    type="certificate-authentication",
                    mutual_authentication=ec2.CfnClientVpnEndpoint.CertificateAuthenticationRequestProperty(
                        client_root_certificate_chain_arn=client_certificate_arn
                    ),
                )
            ],
            connection_log_options=ec2.CfnClientVpnEndpoint.ConnectionLogOptionsProperty(
                enabled=False
            ),
            vpn_port=443,
            security_group_ids=[vpn_security_group.ref],
            vpc_id=vpc.ref,
            split_tunnel=True,
            client_connect_options=ec2.CfnClientVpnEndpoint.ClientConnectOptionsProperty(
                enabled=False
            ),
        )

        id = f"sano-{org}-client-vpn-target-network-association"
        client_vpn_target_network_association = ec2.CfnClientVpnTargetNetworkAssociation(
            self,
            id,
            client_vpn_endpoint_id=client_vpn_endpoint.ref,
            subnet_id=client_vpn_subnet.subnet_id,
        )
        client_vpn_target_network_association.add_depends_on(client_vpn_endpoint)

        id = f"sano-{org}-client-vpn-authorization-rule"
        client_vpn_authorization_rule = ec2.CfnClientVpnAuthorizationRule(
            self,
            id,
            client_vpn_endpoint_id=client_vpn_endpoint.ref,
            target_network_cidr=f"172.{second_8_bits}.0.0/16",
            authorize_all_groups=True,
        )
        client_vpn_authorization_rule.add_depends_on(client_vpn_endpoint)
