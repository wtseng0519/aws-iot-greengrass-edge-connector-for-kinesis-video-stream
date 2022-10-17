import boto3
import sys
import yaml
import os
import json

REGION = os.environ.get('AWS_REGION')
THING_GROUP = os.environ.get('THING_GROUP_NAME')
ACCOUNT_ID = boto3.client('sts').get_caller_identity().get('Account')


class GreenGrassV2Wrapper:
    """
    Encapsulates AWS GreenGrassV2 functions.
    """

    def __init__(self, greengrassv2_client, sitewise_hub_id):
        """
        :param config_client: A Boto3 AWS GreenGrassV2 client.
        """
        self.greengrassv2_client = greengrassv2_client
        self.sitewise_hub_id = sitewise_hub_id
        self.componentConfigs = []
        self.configuration_reader()

    def configuration_reader(self):
        """
        Read configuration from resource_configure.yml file
        """
        with open("./deployment.yml", "r") as stream:
            try:
                configure = yaml.safe_load(stream)
                for key in configure:
                    component = configure.get(key)
                    if component.get("Name") is not None:
                        self.componentConfigs.append(component)
                    else:
                        raise TypeError(key + " must have a Type!")
            except yaml.YAMLError as exc:
                print(exc)
        print(self.componentConfigs)

    def create_deployment(self):
        """
        create a single greengrass v2 deployment with default setting
        """
        DEPLOYMENY_POLICY = {
            "failureHandlingPolicy": "ROLLBACK",
            "componentUpdatePolicy": {
                "action": "NOTIFY_COMPONENTS",
                "timeoutInSeconds": 60
            }
        }
        IOT_JOB_CONFIGURATION = {
            "jobExecutionsRolloutConfig": {
                "maximumPerMinute": 1000
            }
        }
        components = {}

        for component in self.componentConfigs:
            components[component.get("Name")] = {
                "componentVersion": component.get("Version")
            }
            if component.get("Name") == 'aws.iot.EdgeConnectorForKVS':
                components[component.get("Name")] = {
                    "componentVersion": component.get("Version"),
                    "runWith": {
                    },
                    "configurationUpdate": {
                        "merge": json.dumps({
                            "SiteWiseAssetIdForHub": self.sitewise_hub_id
                        })
                    }
                }

        thinggroup_arn = "arn:aws:iot:%s:%s:thinggroup/%s" % (
            REGION, ACCOUNT_ID, THING_GROUP)
        try:
            self.greengrassv2_client.create_deployment(
                targetArn=thinggroup_arn,
                deploymentName='EdgeConnectorForKVS_Deployment',
                components=components,
                iotJobConfiguration=IOT_JOB_CONFIGURATION,
                deploymentPolicies=DEPLOYMENY_POLICY
            )
            print("Created ggv2 deployment successfully")
        except:
            print("Couldn't create configuration deployment")
            raise


if __name__ == "__main__":
    sitewise_hub_id = ""
    with open('var.txt', 'r') as f:
        sitewise_hub_id = f.read()

        deployer = GreenGrassV2Wrapper(
            boto3.client('greengrassv2', region_name=REGION),
            sitewise_hub_id)
        deployer.create_deployment()
