# Sano Genetics Infrastructure Engineer Test

In our GitHub, `/infra` is a repository that contains the code that we use to provision the AWS infrastructure required to run a Portal on the Sano Platform. Our offering currently includes a Python server that we deploy using https://github.com/zappa/Zappa, and two web clients... [one for study participants](https://sanogenetics.org), [and one for site administrators](https://admin.sanogenetics.org) that we host as single page applications using S3 and Cloudfront.

`/infra-config` is another repository that is only stored locally and backed up in a secure location so that we can track changes to our infrastructure and server configuration changes.

This snapshot is non-functional so you won't be able to test it out yourself, but we are hoping you can deduce what you need by inspecting the code and seeing how the resources we are creating are linked to one another within the code.

For additional information, see infra/README.md