# Prerequisite

This is modelled of of deploying as a SAM (Serverless Application Model)
See https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-mac.html

1. Go to AWS and get a IAM in Administrator user group
2. Install Docker Desktop
3. Install Homebrew. Using 3.6.1 at time of writing
4. Instal AWS SAM CLI

# Debugging

- Install the AWS Toolkit for VSCode

- Run the VSCode debug config "KickerFunction"

# Deploying

- Validate template `sam validate`

- Build First `sam build`

- Start local DynamoDB `docker-compose up`

- Test locally `sam local start-api --profile personal`

- When all is good deploy `sam deploy --profile personal`

## Checking Deployment

**List Functions**
`aws lambda list-functions --profile personal`

**Invoke Function**
`aws lambda invoke --profile personal --function-name padding-KickerFunction-iEjL2UkRuFKS --cli-binary-format raw-in-base64-out --payload '{"queryStringParameters": {"angle": "55","height": "6"}}' response.json`

# CI/CD SEtup

- `sam pipeline init --bootstrap`

- Choose "1. AWS Quick Start ..."

- Choose "3. GitHub Actions"

- Named the Stage 1 "dev"

- Used my personal profile, region: us-west-2

- Had it create the IAM user

- Had it create the pipeline execution role and CloudFormation role and bucket

```sh
[4] Summary
Below is the summary of the answers:
        1 - Account: 994253025710
        2 - Stage configuration name: dev
        3 - Region: us-west-2
        4 - Pipeline user: [to be created]
        5 - Pipeline execution role: [to be created]
        6 - CloudFormation execution role: [to be created]
        7 - Artifacts bucket: [to be created]
        8 - ECR image repository: [skipped]
```

- Ran through `sam pipeline init --bootstrap` again and created a `prod` stage. I created new build resources.

- GitHub secrets

  - Create a Repository secret for "AWS_ACCESS_KEY_ID" and "AWS_ACCESS_SECRET_KEY". I used a random UUID for each but I think the --bootstrap script will populate these autmatically. I have to put in the creds from `ws-sam-cli-managed-dev-pipeline-reso-PipelineUser-JBWUOJR6OKF8`

- After it creates the `samconifg.toml` file edit it and make `confirm_changeset` false is in the default environment.

- Make sure you delete the existing stack if there is one.

FOO
