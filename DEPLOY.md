# Prerequisite

This is modelled of of deploying as a SAM (Serverless Application Model)
See https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-mac.html

1. Go to AWS and get a IAM in Administrator user group
2. Install Docker Desktop
3. Install Homebrew. Using 3.6.1 at time of writing
4. Instal AWS SAM CLI

# Debugging

- Install the AWS Toolkit for VSCode

-

# Deploying

- Validate template `sam validate`

- Build First `sam build`

- Test locally `sam local start-api`

- When all is good deploy `sam deploy --profile personal`

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

- Now set up CI/CD
  - [See Step 2 here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-generating-example-ci-cd-others.html)
