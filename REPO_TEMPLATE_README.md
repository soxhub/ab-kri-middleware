# Internal Apps Template
This repository is a template that should be used to create new repositorys for internal applications.

## What is an Internal Application?
These are applications that are _not_ customer facing applications. These applications are generally built to improve the workflow of our internal employees. Generally, the default location these internal applications are deployed to is the Corporate/Internal Apps Kubernetes cluster.

Some examples include Galaxy, Bug Tracker, and AuditBoard Home.

## Internal Apps Deployment Workflow
This workflow is designed for internal apps that will benefit from having a development site before changes get pushed to a production/live site. If this workflow doesn't fit your use case please check out the [static sites template repository (to be created)](https://www.google.com).

* Any push commit in any branch -> trigger build pipeline
* Merge into master -> trigger deployment to dev site `{internal_app}.dev.auditboardteam.com`
* GitHub Release -> trigger deployment to prod site `{internal_app}.auditboardteam.com`

## Set up
1. Select this Template when creating a new GitHub repository
2. In your new GitHub Repository, go to `Settings>Secrets` and create a new secret named `CODEFRESH_API_TOKEN`. The secret value will be stored in LastPass under `Codefresh API Token for GitHub Actions`.
3. Create a new helm chart in the [helm charts repository](https://github.com/soxhub/helm-charts)
Note: Please name the helm chart the same name as the repository for your project
4. Create a (Quay)[https://quay.io] image repository for docker images. Currently you will need to reach out to the DevOps/Platform team for help setting this up.
* Update the `soxhub+codefresh` quay robot account to have read/write access to the new quay image repo. 
* Update the `soxhub+corp` quay robot account to have read access to the new quay image repo. 
5. In your Github Actions workflow `.github/workflows/main.yaml`, update anywhere that has the `<INSERT>` with the correct value.
6. If this application requires an AWS dependency (postgres db, s3 bucket), please reach out to DevOps/Platform team for help setting this up.
7. For environment variables and secrets, we are currently using [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/). Please reach out to the DevOps/Platform team for help setting this up.


### Improvements 
In an ideal scenario, cloning this repo template and minor application specific configuration _should_ be all that is necessary to setting up a new internal app for build and deploy. Unfortunately there are still some areas for improvement to get to this state. 

* **Generic internal apps helm chart:** with a generic helm chart, we don't necessarily need a new helm chart for each new application. However, achieving a generic helm chart is _quite_ difficult as applications can differ in dependencies. (does it need a redis deployment? does it need a volume mount?) To achieve this, we could end up with multiple generic helm charts or another possibility is to generate the helm chart config.

* **Automatic creation of backend cloud depenedencies:** it would be nice to be able to provision popular backend dependencies in the cloud (Postgres DB, S3 Bucket) thru configuration set via this repository template. One possible way to achieve this, we would have a buildpack-esque config that allows us to set fields like `require_postgres_db: true` which would invoke a Codefresh pipeline to create the database and add the database url to secrets manager.

* **Easier environment variable management:** right now, all env vars and secrets are stored in AWS Secrets Manager, which many developers have limited access to. A OneLogin authed env vars service that has access to write/update to AWS Secrets Manager could work.

* **Pipeline to set the Codefresh API token for your Github repo:** right now, step 2 in Setup requires going to LastPass to grab the API secret and setting it as a secret in your new Github repository. We could have a GitHub repo in which you create a PR that once merged kicks off a pipeline to add the Codefresh API token to your new repository.

* **Automatic quay image repository creation:** currently we are creating new quay.io image repositories manually in the web interface. Being able to create this automatically when a new project is created would be splendid.