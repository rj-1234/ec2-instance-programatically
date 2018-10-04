
import sys
import boto3
import os
from random import *


"""
Incorrect usage of the script
"""

def panic():
	print("Something went wrong!!! \n To List all available instances use - python ec2-launch.py -l \n To create a new Instance use - python ec2-launch.py -c \n To terminate an existing instance use - python ec2-launch.py -t [instanceId]")


"""
Tries to terminate the supplied instance
"""

def terminate_instance(InstanceId):
	print("Terminating Instance : ", InstanceId)
	try:
		ec2 = boto3.resource('ec2')
		instance = ec2.Instance(InstanceId)
		response = instance.terminate()
		print("Instance Terminated:\n",response)
	except:
		print("Failed to terminate instance: ", InstanceId)


"""
Tries to create a new instance and return instance id, otherwise returns false
"""

def create_instance(KeyPair, GroupId):
	print("Creating a new instance: \n")
	try:
		ec2 = boto3.resource('ec2')
		instance = ec2.create_instances(ImageId='ami-97785bed', MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName = KeyPair, SecurityGroupIds = [GroupId])
		print("Instance ID : ",instance[0].id, " ", instance[0].public_ip_address, instance[0].public_dns_name)
		return True, instance[0].id
	except:
		return False, "Failed to create instance"


"""
List all instances
"""

def list_instances():
	print("List of all available instances: \n");
	ec2 = boto3.resource('ec2')
	for instance in ec2.instances.all():
		print("Instance ID : ",instance.id, 
				"\nState : ", instance.state,
				"\nLocation : ", instance.placement['AvailabilityZone'], 
				"\nIP : ", instance.public_ip_address, 
				"\nPublic DNS:", instance.public_dns_name)

"""
Delete the keypair to avoid generating a bunch of keypair values for every run
"""

def delete_key_pair(KeyName):
	try:
		if os.path.exists(KeyName+".pem"):
			os.remove(KeyName+".pem")
		else:
			pass
		ec2 = boto3.client('ec2')
		ec2.delete_key_pair(KeyName=KeyName)

	except:
		print("Failed to delete key pair")

"""
Tries to create a new(random) security group to be used
"""

def create_security_group(GroupName, GroupDescription):
	try:
		print("Initiating security group creation....")
		ec2 = boto3.resource('ec2')
		CustomSecGroup = ec2.create_security_group(GroupName=GroupName+str(randint(1,1000)), Description=GroupDescription)
		CustomSecGroup.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
		return True, CustomSecGroup.id

	except:
		return False, "Failed to create Security Group"

"""
Create a new KeyPair, or recreates it after deleting the existing one
"""

def create_key_pair(KeyName):
	print("Creating new key pair....")
	try:
		delete_key_pair(KeyName)
		ec2 = boto3.resource('ec2')
		PrivatePemFile = open(KeyName+'.pem','w')
		key_pair_variable = ec2.create_key_pair(KeyName=KeyName)
		KeyPairPrivate = str(key_pair_variable.key_material)
		PrivatePemFile.write(KeyPairPrivate)
		return True

	except:
		return False

def main():
	if len(sys.argv)<2 :
		panic()
		sys.exit(1)

	if sys.argv[1] == "-t" and len(sys.argv)<3:
		panic()
		sys.exit(1)

	KeyName = "HW1_ec2_instance"
	InstanceId = ""

	if sys.argv[1] == '-l':
		list_instances()

	elif sys.argv[1] == "-c":

		if create_key_pair(KeyName) == False:
			print("Failed to create KeyPair : ", KeyName)

		return_Value, Security_GroupId = create_security_group("CustomSecGroup", "CustomSec Group for newly created VM instance")
		if return_Value == False:
			print (Security_GroupId)
			sys.exit(1)

		return_Value, InstanceId = create_instance(KeyName, Security_GroupId)
		if return_Value == False:
			print ("Failed to Created Instance", InstanceId)
			sys.exit(1)
		list_instances()


	elif sys.argv[1] == '-t':
		InstanceId = sys.argv[2]
		terminate_instance(InstanceId)
		delete_key_pair(KeyName)
		list_instances()

	else:
		panic()


if __name__ == '__main__':main()