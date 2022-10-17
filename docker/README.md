# Running AWS IoT Greengrass V2 in a Docker Container

## Overview

AWS IoT Greengrass can run in a Docker container. You can use the Dockerfile in this package to build a container image that runs on `x86_64` platforms.

This guide will show you how to:

- Build a Docker image from the Dockerfile for Amazon Linux 2 `x86_64`.
- Run an Amazon Linux Docker image containing AWS IoT Greengrass V2.
- Use `docker-compose` to build and run AWS IoT Greengrass V2 in the Docker container.
- The Docker image supports Mac OSX, and Linux as Docker host platforms to run the Greengrass core software.

## Prerequisites

- Mac OSX or Linux host computer running Docker and Docker Compose (optional).
- The Docker installation (version 18.09 or later) can be found [here](https://docs.docker.com/install/).
- The Docker Compose installation (version 1.22 or later) can be found [here](https://docs.docker.com/compose/install/).
  Docker for Mac OS and Docker Toolbox include Compose, so those platforms don't need a separate Compose installation. Note: You must have version 1.22 or later because `init` support is required.

## Running AWS IoT Greengrass SiteWatch Component in a Docker Container

The following steps show how to build the Docker image from the Dockerfile and configure AWS IoT Greengrass and SiteWatch to run in a Docker container.  
User Onboarding Journey (Option 5)

### Step 0. Clone the Open Source repo from github

### Step 1. Configure your AWS credentials

In this step, you create a credential file on the host computer that contains your AWS security credentials. When you run the AWS IoT Greengrass Docker image, you must mount the folder that contains this credential file to /root/.aws/ in the Docker container. The AWS IoT Greengrass installer uses these credentials to provision resources in your AWS account.
Retrieve one of the following.

(Recommended) Temporary credentials for an IAM role. For information about how to retrieve temporary credentials, see Using temporary security credentials with the AWS CLI (https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html#using-temp-creds-sdk-cli) in the IAM User Guide.
Create a folder where you place your credential file.

```
mkdir ./greengrass-v2-credentials
```

Use a text editor to create a configuration file named credentials in the ./greengrass-v2-credentials folder.
For example, you can run the following command to use GNU nano to create the credentials file.

```
nano ./greengrass-v2-credentials/credentials
```

Add your AWS credentials to the credentials file in the following format.

```
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws_session_token = AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk
```

Include aws_session_token for temporary credentials only.
_Note_
Remove the credential file from the host computer after you start the AWS IoT Greengrass container. If you don't remove the credential file, then your AWS credentials will remain mounted inside the container. For more information, see Run the AWS IoT Greengrass Core software in a container (https://docs.aws.amazon.com/greengrass/v2/developerguide/run-greengrass-docker-automatic-provisioning.html#run-greengrass-image-automatic-provisioning).

### Step 2. Create an environment file

Uses an environment file to set the environment variables that will be passed to the AWS IoT Greengrass Core software installer inside the Docker container. You can also use the -e or --env argument (https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file) in your docker run command to set environment variables in the Docker container or you can set the variables in an environment block (https://docs.docker.com/compose/compose-file/compose-file-v3/#environment) in the docker-compose.yml file.
Use a text editor to create an environment file named .env.
For example, on a Linux-based system, you can run the following command to use GNU nano to create the .env in the current directory.

```
nano .env
```

Copy the following content into the file.

```
GGC_ROOT_PATH=/greengrass/v2
AWS_REGION=region
PROVISION=true
THING_NAME=MyGreengrassCore
THING_GROUP_NAME=MyGreengrassCoreGroup
TES_ROLE_NAME=GreengrassV2TokenExchangeRole
TES_ROLE_ALIAS_NAME=GreengrassCoreTokenExchangeRoleAlias
COMPONENT_DEFAULT_USER=ggc_user:ggc_group
```

Then, replace the following values if needed.
/greengrass/v2. The Greengrass root folder that you want to use for installation. You use the GGC_ROOT environment variable to set this value.
region. The AWS Region where you created the resources.
MyGreengrassCore. The name of the AWS IoT thing. If the thing doesn't exist, the installer creates it. The installer downloads the certificates to authenticate as the AWS IoT thing.
MyGreengrassCoreGroup. The name of the AWS IoT thing group. If the thing group doesn't exist, the installer creates it and adds the thing to it. If the thing group exists and has an active deployment, the core device downloads and runs the software that the deployment specifies.
GreengrassV2TokenExchangeRole. Replace with the name of the IAM token exchange role that allows the Greengrass core device to get temporary AWS credentials. If the role doesn't exist, the installer creates it and creates and attaches a policy named GreengrassV2TokenExchangeRoleAccess. For more information, see Authorize core devices to interact with AWS services (https://docs.aws.amazon.com/greengrass/v2/developerguide/device-service-role.html).
GreengrassCoreTokenExchangeRoleAlias. The token exchange role alias. If the role alias doesn't exist, the installer creates it and points it to the IAM token exchange role that you specify. For more information, see

### Step 3. Build and deploy docker

**3.1** Make changes to resource_configure.yml with your RTSP url and camera settings.

**3.2**
Build docker image using docker-compose

```
docker-compose -f docker-compose.yml build
```

**3.3**
Run docker using docker-compose

```
docker-compose -f docker-compose.yml up
```

**3.4** The output should look like this example:

```
Running Greengrass with the following options: -Droot=/greengrass/v2 -Dlog.store=FILE -Dlog.level= -jar /opt/greengrassv2/lib/Greengrass.jar --provision true --deploy-dev-tools false --aws-region us-east-1 --start false
Installing Greengrass for the first time...
...
...
Launching Nucleus...
Launched Nucleus successfully.
```

- **WARNING**: We strongly recommend removing this credential file from your host after the initial setup, as further authorization will be handled by the Greengrass Token Exchange Service using X.509 certificates. For more information, [see how Greengrass interacts with AWS services](https://docs.aws.amazon.com/greengrass/v2/developerguide/interact-with-aws-services.html) .
- If you would like to override any of the default configuration options or use your own config file to start Greengrass, specify those environment variables in the `environment` section as well. If you wish to use your own init config file, you must mount it to the directory you specify in the `INIT_CONFIG` environment variable, as well as mounting any extra files (e.g. custom certificates) you refer to in the init config file.  
  Please see [the installer documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/configure-installer.html) for configuration options and behavior.

### Debugging the Docker Container

To debug issues with the container, you can persist the runtime logs or attach an interactive shell.

#### Persist Greengrass Runtime Logs outside the Greengrass Docker Container

You can run the AWS IoT Greengrass Docker container after bind-mounting the `/greengrass/v2/logs` directory to persist logs even after the container has exited or is removed. Alternatively, you can omit the `--rm` flag and use `docker cp` to copy the logs back from the container after it exits.

#### Attach an Interactive Shell to the Greengrass Docker Container

You can attach an interactive shell to a running AWS IoT Greengrass Docker container. This can help you to investigate the state of the Greengrass Docker container.  
Either use `docker attach` or run the following command in the terminal.

```
docker exec -it container-name sh -c "YOUR_COMMAND > /proc/1/fd/1"
```

- This ensures that all output is redirected to PID 1 and will show up in the docker logs.

### Stopping the Docker Container

To stop the AWS IoT Greengrass Docker Container, press Ctrl+C in your terminal (interactive mode) or run `docker stop` or `docker-compose stop` (detached mode).

This action will send SIGTERM to the Greengrass process to gracefully shut down down the Greengrass process and all subprocesses that were started. The Docker container is initialized with the docker-init executable as process PID 1, which helps in removing any leftover zombie processes. For more information, see the [Docker documentation for init](https://docs.docker.com/engine/reference/run/#specify-an-init-process).

You may use `docker start` or `docker-compose start` to restart a stopped container.

### Removing the Docker Container

If you have not specified the `--rm` flag in your `docker run` command, your container will remain in the STOPPED state on your host. Use `docker rm` or `docker-compose down` to remove your container.
