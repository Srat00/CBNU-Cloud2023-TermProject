import boto3
import paramiko
import getpass
from botocore.exceptions import ClientError

class AWSResourceManager:
    def __init__(self, access, secret, region='ap-southeast-2'):
        self.ec2 = boto3.resource('ec2', region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)
        self.ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)
        self.condor_pool = 'ec2-54-79-63-34.ap-southeast-2.compute.amazonaws.com'

    def list_instances(self):
        instances = self.ec2.instances.all()
        for instance in instances:
            # 인스턴스 이름 파싱
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
                else:
                    instance_name = 'N/A'

            print(f"Instance ID: {instance.id} | Name : {instance_name} | Status: {instance.state['Name']}")

    def list_available_zones(self):
        response = self.ec2_client.describe_availability_zones()
        for zone in response['AvailabilityZones']:
            print(f"Zone: {zone['ZoneName']} | State: {zone['State']}")

    def list_available_regions(self):
        regions = self.ec2_client.describe_regions()
        for region in regions['Regions']:
            print(f"Region: {region['RegionName']}")

    def manage_instance(self, instance_id, type):
        try:
            if type == 1:
                # 인스턴스 시작 요청
                self.ec2.instances.filter(InstanceIds=[instance_id]).start()
                print(f"Starting {instance_id}...")
            elif type == 2:
                self.ec2.instances.filter(InstanceIds=[instance_id]).stop()
                print(f"Stopping {instance_id}...")
            elif type == 3:
                self.ec2.instances.filter(InstanceIds=[instance_id]).reboot()
                print(f"Rebooting {instance_id}...")

        except ClientError as e:
            # 예외 처리
            error_message = str(e.response.get('Error', {}).get('Message', 'Unknown error'))
            print(f"Failed. | {error_message}")

    def create_instance(self, name):
        # 인스턴스 생성 요청
        self.ec2.create_instances(
            ImageId='ami-0f5f922f781854672', #Amazon Linux 2 Kernel 5.10 AMI 2.0.20231116.0 x86_64 HVM gp2
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='rockyeo',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ]
        )

        print(f"{name} Instance Created.")


        
    def list_images(self):
        images = self.ec2.images.all()
        for image in images:
            print(f"Image ID: {image.id}, Name: {image.name}")

    def condor_status(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.condor_pool, username='ec2-user', key_filename='C:/.ssh/rockyeo.pem')
        stdin, stdout, stderr = ssh.exec_command('condor_status')
        lines = stdout.readlines()
        ssh.close()
        return lines
    

def main():
    print("      __          _______   __  __                                   \n")
    print("     /\ \        / / ____| |  \/  |                                  \n")
    print("    /  \ \  /\  / / (___   | \  / | __ _ _ __   __ _  __ _  ___ _ __ \n")
    print("   / /\ \ \/  \/ / \___ \  | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|\n")
    print("  / ____ \  /\  /  ____) | | |  | | (_| | | | | (_| | (_| |  __/ |   \n")
    print(" /_/    \_\/  \/  |_____/  |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   \n")
    print("                                                      __/ |          \n")
    print("   2020039091 Rocky Eo                               |___/   ")
    
    access = input("Access Key : ")
    secret = getpass.getpass("Secret Key : ")

    aws_manager = AWSResourceManager(access, secret)

    while True:
        print("\n------------------------------------------------------------")
        print("1. list instances\t2. available zones")
        print("3. start instance\t4. available regions")
        print("5. stop instance\t6. create instance")
        print("7. reboot instance\t8. list images")
        print("9. condor status")
        print("99. quit")
        print("------------------------------------------------------------")

        choice = input("Select Menu : ")

        if choice == '1':
            aws_manager.list_instances()

        elif choice == '2':
            aws_manager.list_available_zones()

        elif choice == '3':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 1)

        elif choice == '4':
            aws_manager.list_available_regions()

        elif choice == '5':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 2)

        elif choice == '6':
            instance_name = input("Instance Name : ")
            aws_manager.create_instance(instance_name)

        elif choice == '7':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 3)

        elif choice == '8':
            aws_manager.list_images()
        
        elif choice == '9':
            condor_status = aws_manager.condor_status()
            print(*condor_status)

        elif choice == '99':
            break
        else:
            print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()
