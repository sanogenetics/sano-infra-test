from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk


class VpcStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        org,
        region,
        second_8_bits,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        id = f"sano-{org}-vpc"
        self.vpc = ec2.CfnVPC(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            cidr_block=f"172.{second_8_bits}.0.0/16",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            instance_tenancy="default",
        )

        id = f"sano-{org}-internet-gateway"
        self.internet_gateway = ec2.CfnInternetGateway(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
        )

        id = f"sano-{org}-vpc-gateway-attachment"
        vpc_gateway_attachment = ec2.CfnVPCGatewayAttachment(
            self,
            id,
            internet_gateway_id=self.internet_gateway.ref,
            vpc_id=self.vpc.ref,
        )

        id = f"sano-{org}-nat-gatway-eip"
        nat_gateway_eip = ec2.CfnEIP(
            self, id, tags=[cdk.CfnTag(key="Name", value=id)], domain="vpc"
        )

        id = f"sano-{org}-nat-subnet"
        nat_subnet = ec2.PrivateSubnet(
            self,
            id,
            availability_zone=f"{region}b",
            cidr_block=f"172.{second_8_bits}.49.0/24",
            vpc_id=self.vpc.ref,
            map_public_ip_on_launch=False,
        )

        id = f"sano-{org}-nat-gateway"
        self.nat_gateway = ec2.CfnNatGateway(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            subnet_id=nat_subnet.subnet_id,
            allocation_id=nat_gateway_eip.attr_allocation_id,
        )

        id = f"sano-{org}-nat-subnet-route"
        nat_subnet_route = ec2.CfnRoute(
            self,
            id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.internet_gateway.ref,
            route_table_id=nat_subnet.route_table.route_table_id,
        )
        nat_subnet_route.add_depends_on(vpc_gateway_attachment)
