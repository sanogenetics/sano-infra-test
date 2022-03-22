from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk


class MediaStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        org,
        envir,
        region,
        domain,
        media_subdomain,
        certificate_arn,
        add_aliases,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        SOE = f"sano-{org}-{envir}"
        s3_bucket_origin_id = f"{SOE}-media-s3-bucket-origin"

        id = f"{SOE}-media-s3-bucket"
        media_s3_bucket = s3.CfnBucket(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            bucket_name=f"{SOE}-media-uploads",
            cors_configuration=s3.CfnBucket.CorsConfigurationProperty(
                cors_rules=[
                    s3.CfnBucket.CorsRuleProperty(
                        allowed_headers=["*"],
                        allowed_methods=["GET", "POST", "PUT"],
                        allowed_origins=["*"],
                    )
                ]
            ),
            website_configuration=s3.CfnBucket.WebsiteConfigurationProperty(
                index_document="index.html"
            ),
            versioning_configuration=s3.CfnBucket.VersioningConfigurationProperty(
                status="Enabled"
            ),
        )

        id = f"{SOE}-media-s3-bucket-policy"
        s3.CfnBucketPolicy(
            self,
            id,
            bucket=media_s3_bucket.ref,
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AddPerm",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{SOE}-media-uploads/*",
                    }
                ],
            },
        )

        id = f"{SOE}-media-cloudfront-distribution"
        cloudfront_distribution = cloudfront.CfnDistribution(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                # remove aliases below if domain is already linked with distribution
                aliases=[f"{media_subdomain}{domain}"] if add_aliases == "yes" else [],
                origins=[
                    cloudfront.CfnDistribution.OriginProperty(
                        connection_attempts=3,
                        connection_timeout=10,
                        custom_origin_config=cloudfront.CfnDistribution.CustomOriginConfigProperty(
                            http_port=80,
                            https_port=443,
                            origin_keepalive_timeout=5,
                            origin_protocol_policy="http-only",
                            origin_read_timeout=30,
                            origin_ssl_protocols=["TLSv1", "TLSv1.1", "TLSv1.2"],
                        ),
                        domain_name=f"{media_s3_bucket.bucket_name}.s3-website.{region}.amazonaws.com",
                        id=s3_bucket_origin_id,
                        origin_path="",
                    ),
                ],
                origin_groups={"quantity": 0},
                default_cache_behavior=cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    allowed_methods=["HEAD", "GET"],
                    cached_methods=["HEAD", "GET"],
                    compress=True,
                    default_ttl=0,
                    forwarded_values=cloudfront.CfnDistribution.ForwardedValuesProperty(
                        cookies={"forward": "none"},
                        headers=["Authorization", "Access-Control-Request-Headers"],
                        query_string=True,
                        query_string_cache_keys=["must-put"],
                    ),
                    max_ttl=0,
                    min_ttl=0,
                    smooth_streaming=False,
                    target_origin_id=s3_bucket_origin_id,
                    viewer_protocol_policy="redirect-to-https",
                ),
                cache_behaviors=[
                    cloudfront.CfnDistribution.CacheBehaviorProperty(
                        allowed_methods=["HEAD", "GET"],
                        cached_methods=["HEAD", "GET"],
                        compress=True,
                        default_ttl=0,
                        forwarded_values=cloudfront.CfnDistribution.ForwardedValuesProperty(
                            cookies={"forward": "none"},
                            headers=["Authorization", "Access-Control-Request-Headers"],
                            query_string=True,
                            query_string_cache_keys=["must-put"],
                        ),
                        max_ttl=0,
                        min_ttl=0,
                        path_pattern="/uploads/*",
                        smooth_streaming=False,
                        target_origin_id=s3_bucket_origin_id,
                        viewer_protocol_policy="redirect-to-https",
                    ),
                ],
                comment=f"{SOE}-media",
                price_class="PriceClass_All",
                enabled=True,
                viewer_certificate=cloudfront.CfnDistribution.ViewerCertificateProperty(
                    acm_certificate_arn=certificate_arn,
                    minimum_protocol_version="TLSv1.2_2018",
                    ssl_support_method="sni-only",
                ),
                restrictions=cloudfront.CfnDistribution.RestrictionsProperty(
                    geo_restriction=cloudfront.CfnDistribution.GeoRestrictionProperty(
                        restriction_type="none"
                    )
                ),
                http_version="http2",
                default_root_object="",
                ipv6_enabled=True,
            ),
        )
        cloudfront_distribution.add_depends_on(media_s3_bucket)
