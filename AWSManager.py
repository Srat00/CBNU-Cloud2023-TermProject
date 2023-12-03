import boto3
import paramiko
import getpass
from botocore.exceptions import ClientError

class AWSResourceManager:
    def __init__(self, access, secret, region='ap-southeast-2'):
        # AWS 리소스 생성
        self.ec2 = boto3.resource('ec2', region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)
        self.ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)
        self.s3 = boto3.client('s3', region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)
        # Condor Master IP
        self.condor_pool = 'ec2-54-79-63-34.ap-southeast-2.compute.amazonaws.com'

    # 인스턴스 목록 출력
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

    # 사용 가능한 영역 목록 출력
    def list_available_zones(self):
        response = self.ec2_client.describe_availability_zones()
        for zone in response['AvailabilityZones']:
            print(f"Zone: {zone['ZoneName']} | State: {zone['State']}")

    # 사용 가능한 지역 목록 출력
    def list_available_regions(self):
        regions = self.ec2_client.describe_regions()
        for region in regions['Regions']:
            print(f"Region: {region['RegionName']}")

    # 인스턴스 관리
    def manage_instance(self, instance_id, type):
        try:
            if type == 1:
                # 인스턴스 시작
                self.ec2.instances.filter(InstanceIds=[instance_id]).start()
                print(f"Starting {instance_id}...")
            elif type == 2:
                # 인스턴스 중지
                self.ec2.instances.filter(InstanceIds=[instance_id]).stop()
                print(f"Stopping {instance_id}...")
            elif type == 3:
                # 인스턴스 재부팅
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
            KeyName='rockyeo', # 기존 키페어 재활용
            # 인스턴스에 태그 추가
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

    # 이미지 목록 출력
    def list_images(self):
        images = self.ec2.images.all()
        for image in images:
            print(f"Image ID: {image.id}, Name: {image.name}")
   
    # condor_status 명령어 실행
    def condor_status(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.condor_pool, username='ec2-user', key_filename='C:/.ssh/rockyeo.pem')
        stdin, stdout, stderr = ssh.exec_command('condor_status')
        lines = stdout.readlines()
        ssh.close()
        return lines
    
    # S3 객체 목록 출력
    def list_s3_objects(self, bucket_name):
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)

            for obj in response.get('Contents', []):
                print(f"File Name: {obj['Key']} | Last Modified: {obj['LastModified']}")
        except ClientError as e:
            error_message = str(e.response.get('Error', {}).get('Message', 'Unknown error'))
            print(f"Failed. | {error_message}")

    # S3 업로드
    def upload_to_s3(self, bucket_name, local_file, s3_file_name):
        try:
            self.s3.upload_file(local_file, bucket_name, s3_file_name)
            print(f"{local_file} Uploaded")
        except ClientError as e:
            error_message = str(e.response.get('Error', {}).get('Message', 'Unknown error'))
            print(f"Failed. | {error_message}")

    # S3 다운로드
    def download_from_s3(self, bucket_name, s3_file_name, local_file):
        try:
            self.s3.download_file(bucket_name, s3_file_name, local_file)
            print(f"{s3_file_name} Downloaded")
        except ClientError as e:
            error_message = str(e.response.get('Error', {}).get('Message', 'Unknown error'))
            print(f"Failed. | {error_message}")
    
    # S3 객체 삭제       
    def remove_s3_object(self, bucket_name, key):
        try:
            # S3 버킷에서 객체 삭제
            self.s3.delete_object(Bucket=bucket_name, Key=key)
            print(f"{key} Deleted.")
        except ClientError as e:
            error_message = str(e.response.get('Error', {}).get('Message', 'Unknown error'))
            print(f"Failed. | {error_message}")

def main():
    print("    ___      _____ __  __                             ")
    print("   /_\ \    / / __|  \/  |__ _ _ _  __ _ __ _ ___ _ _ ")
    print("  / _ \ \/\/ /\__ \ |\/| / _` | ' \/ _` / _` / -_) '_|")
    print(" /_/ \_\_/\_/ |___/_|  |_\__,_|_||_\__,_\__, \___|_|  ")
    print(" 2020039091 Rocky Eo                    |___/      \n")
    
    # AWS 인증 정보 입력, 보안을 위해 직접 입력식으로 변경, getpass 모듈 사용
    access = input("Access Key : ")
    secret = getpass.getpass("Secret Key : ")

    aws_manager = AWSResourceManager(access, secret)

    while True:
        print("\n------------------------------------------------------------")
        print("1. list instances\t2. available zones")
        print("3. start instance\t4. available regions")
        print("5. stop instance\t6. create instance")
        print("7. reboot instance\t8. list images")
        print("9. condor status\t10. list from s3 storage")
        print("11. upload to s3\t12. download from s3")
        print("13. remove from s3")
        print("99. quit")
        print("------------------------------------------------------------")

        choice = input("Select Menu : ")

        # List Instances
        if choice == '1':
            aws_manager.list_instances()

        # Available Zones
        elif choice == '2':
            aws_manager.list_available_zones()

        # Start Instance
        elif choice == '3':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 1)

        # Available Regions
        elif choice == '4':
            aws_manager.list_available_regions()

        # Stop Instance
        elif choice == '5':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 2)

        # Create Instance
        elif choice == '6':
            instance_name = input("Instance Name : ")
            aws_manager.create_instance(instance_name)

        # Reboot Instance
        elif choice == '7':
            instance_id = input("Instance ID : ")
            aws_manager.manage_instance(instance_id, 3)

        # List Images
        elif choice == '8':
            aws_manager.list_images()

        # Condor Status
        elif choice == '9':
            condor_status = aws_manager.condor_status()
            print(*condor_status)

        # List from S3 Storage
        elif choice == '10':
            bucket_name = input("Bucket Name : ")
            aws_manager.list_s3_objects(bucket_name)

        # Upload to S3
        elif choice == '11':
            bucket_name = input("Bucket Name : ")
            local_file = input("Upload File Location ( Example: C:\Test.txt ) : ")
            s3_file_name = input("S3 File Name : ")
            aws_manager.upload_to_s3(bucket_name, local_file, s3_file_name)

        # Download from S3
        elif choice == '12':
            bucket_name = input("Bucket Name : ")
            s3_file_name = input("S3 File Name : ")
            local_file = input("Download File Location ( Example: C:\Test.txt ): ")
            aws_manager.download_from_s3(bucket_name, s3_file_name, local_file)

        # Remove from S3
        elif choice == '13':
            bucket_name = input("Bucket Name : ")
            key = input("S3 File Name : ")
            aws_manager.remove_s3_object(bucket_name, key)
        
        # Quit
        elif choice == '99':
            break
        
        # Invalid Input
        else:
            print("Invalid Input, Please Try Again.")

if __name__ == "__main__":
    main()
