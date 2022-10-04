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
