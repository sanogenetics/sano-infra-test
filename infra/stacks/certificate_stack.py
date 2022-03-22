from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import core as cdk


class CertificateStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        org,
        domains,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        id = f"sano-{org}-certificate-{domains[0].replace('.', '-')}"
        certificatemanager.CfnCertificate(
            self,
            id,
            tags=[cdk.CfnTag(key="Name", value=id)],
            domain_name=domains[0],
            subject_alternative_names=domains,
            domain_validation_options=[
                certificatemanager.CfnCertificate.DomainValidationOptionProperty(
                    domain_name=domain,
                    validation_domain=domain,
                )
                for domain in domains
            ],
            certificate_transparency_logging_preference="ENABLED",
        )
