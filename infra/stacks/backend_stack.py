from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk


class BackendStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        org,
        envir,
        region,
        vpc: ec2.Vpc,
        nat_gateway: ec2.CfnNatGateway,
        second_8_bits,
        db_username,
        db_password,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        SOE = f"sano-{org}-{envir}"
        offset = {"dev": 0, "staging": 20, "prod": 40}[envir]

        id = f"{SOE}-lambda-security-group"
        ec2.CfnSecurityGroup(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            group_description=id,
            group_name=id,
            vpc_id=vpc.ref,
            security_group_egress=[
                ec2.CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ip="0.0.0.0/0",
                )
            ],
        )

        id = f"{SOE}-db-security-group"
        db_security_group = ec2.CfnSecurityGroup(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            group_description=id,
            group_name=id,
            vpc_id=vpc.ref,
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ip="0.0.0.0/0",
                    from_port=5432,
                    to_port=5432,
                ),
            ],
            security_group_egress=[
                ec2.CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ip="0.0.0.0/0",
                )
            ],
        )

        id = f"{SOE}-db-subnet-1"
        third_eight_bits = str(50 + offset + 0)
        db_subnet_1 = ec2.PrivateSubnet(
            self,
            id,
            availability_zone=f"{region}b",
            cidr_block=f"172.{second_8_bits}.{third_eight_bits}.0/24",
            vpc_id=vpc.ref,
        )

        id = f"{SOE}-db-subnet-1-route"
        ec2.CfnRoute(
            self,
            id,
            route_table_id=db_subnet_1.route_table.route_table_id,
            destination_cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateway.ref,
        )

        id = f"{SOE}-db-subnet-2"
        third_eight_bits = str(50 + offset + 1)
        db_subnet_2 = ec2.PrivateSubnet(
            self,
            id,
            availability_zone=f"{region}a",
            cidr_block=f"172.{second_8_bits}.{third_eight_bits}.0/24",
            vpc_id=vpc.ref,
        )

        id = f"{SOE}-db-subnet-2-route"
        ec2.CfnRoute(
            self,
            id,
            route_table_id=db_subnet_2.route_table.route_table_id,
            destination_cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateway.ref,
        )

        id = f"{SOE}-db-subnet-3"
        third_eight_bits = str(50 + offset + 2)
        db_subnet_3 = ec2.PrivateSubnet(
            self,
            id,
            availability_zone=f"{region}c",
            cidr_block=f"172.{second_8_bits}.{third_eight_bits}.0/24",
            vpc_id=vpc.ref,
        )

        id = f"{SOE}-db-subnet-3-route"
        ec2.CfnRoute(
            self,
            id,
            route_table_id=db_subnet_3.route_table.route_table_id,
            destination_cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateway.ref,
        )

        id = f"{SOE}-rds-db-subnet-group"
        db_subnet_group = rds.CfnDBSubnetGroup(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            db_subnet_group_description=id,
            db_subnet_group_name=id,
            subnet_ids=[
                db_subnet_1.subnet_id,
                db_subnet_2.subnet_id,
                db_subnet_3.subnet_id,
            ],
        )

        id = f"{SOE}-rds-db-instance"
        db_instance = rds.CfnDBInstance(
            self,
            id,
            tags=[
                cdk.CfnTag(key="Name", value=id),
                cdk.CfnTag(key="workload-type", value="other"),
            ],
            db_instance_identifier=f"{SOE}-db",
            allocated_storage="20",
            db_instance_class="db.t2.micro",
            engine="postgres",
            master_username=db_username,
            master_user_password=db_password,
            db_name=f"{envir}",
            preferred_backup_window="01:32-02:02",
            backup_retention_period=7,
            availability_zone=f"{region}b",
            preferred_maintenance_window="tue:03:43-tue:04:13",
            multi_az=False,
            engine_version="12.8",
            auto_minor_version_upgrade=True,
            license_model="postgresql-license",
            publicly_accessible=True,
            storage_type="gp2",
            port="5432",
            storage_encrypted=False,
            copy_tags_to_snapshot=True,
            monitoring_interval=0,
            enable_iam_database_authentication=False,
            enable_performance_insights=False,
            deletion_protection=False,
            db_subnet_group_name=f"{SOE}-rds-db-subnet-group",
            vpc_security_groups=[db_security_group.ref],
            db_parameter_group_name="default.postgres12",
            option_group_name="default:postgres-12",
            ca_certificate_identifier="rds-ca-2019",
        )
        db_instance.add_depends_on(db_subnet_group)

        id = f"{SOE}-uploads-s3-bucket"
        s3.CfnBucket(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            bucket_name=f"{SOE}-uploads",
            cors_configuration=s3.CfnBucket.CorsConfigurationProperty(
                cors_rules=[
                    s3.CfnBucket.CorsRuleProperty(
                        allowed_headers=["*"],
                        allowed_methods=["GET", "POST", "PUT"],
                        allowed_origins=["*"],
                    )
                ]
            ),
            versioning_configuration=s3.CfnBucket.VersioningConfigurationProperty(
                status="Suspended"
            ),
        )
