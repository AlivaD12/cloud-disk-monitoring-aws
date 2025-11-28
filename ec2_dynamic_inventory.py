#!/usr/bin/env python3
"""
Ansible Dynamic Inventory Script for AWS EC2 Instances
Returns all running EC2 instances across multiple regions
"""

import json
import boto3
import os

class EC2Inventory:
    def __init__(self):
        # You can set AWS profile via environment variable
        self.aws_profile = os.getenv('AWS_PROFILE', 'default')
        self.session = boto3.Session(profile_name=self.aws_profile)
        self.regions = ['us-east-1', 'us-west-2']  # Add more regions as needed

    def get_instances(self):
        """Discover all running EC2 instances across regions"""
        hosts = {
            '_meta': {
                'hostvars': {}
            },
            'all': {
                'hosts': [],
                'children': ['aws_ec2']
            },
            'aws_ec2': {
                'hosts': [],
                'vars': {
                    'ansible_connection': 'aws_ssm',
                    'ansible_user': 'ubuntu'  # Adjust based on your AMI
                }
            },
            'monitoring_group': {
                'hosts': [],
                'vars': {
                    'disk_monitoring': 'enabled'
                }
            }
        }

        for region in self.regions:
            try:
                ec2 = self.session.resource('ec2', region_name=region)
                instances = ec2.instances.filter(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
                )

                for instance in instances:
                    instance_id = instance.id
                    hosts['all']['hosts'].append(instance_id)
                    hosts['aws_ec2']['hosts'].append(instance_id)
                    hosts['monitoring_group']['hosts'].append(instance_id)

                    # Add host variables
                    hosts['_meta']['hostvars'][instance_id] = {
                        'ansible_host': instance_id,  # SSM uses instance ID
                        'instance_id': instance_id,
                        'instance_type': instance.instance_type,
                        'region': region,
                        'availability_zone': instance.placement['AvailabilityZone'],
                        'private_ip': instance.private_ip_address,
                        'public_ip': instance.public_ip_address if instance.public_ip_address else None,
                        'tags': {tag['Key']: tag['Value'] for tag in instance.tags} if instance.tags else {}
                    }

            except Exception as e:
                print(f"Error querying region {region}: {str(e)}", file=sys.stderr)
                continue

        return hosts

def main():
    import sys
    
    inventory = EC2Inventory()
    
    # Check for --list argument (Ansible standard)
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        print(json.dumps(inventory.get_instances(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        # Return empty dict for single host (not implemented for simplicity)
        print(json.dumps({}))
    else:
        print("Usage: {} --list".format(sys.argv[0]))
        print("Usage: {} --host <hostname>".format(sys.argv[0]))
        sys.exit(1)

if __name__ == '__main__':
    main()