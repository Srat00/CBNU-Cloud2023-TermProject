import boto3

class AWSResourceManager:
    def __init__(self, region='ap-southeast-2a'):
        self.ec2 = boto3.resource('ec2', region_name=region, aws_access_key_id='SECRET', aws_secret_access_key='SECRET')
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.condor_pool = "ip-172-31-3-10.ap-southeast-2.compute.internal"

    def list_instances(self):
        instances = self.ec2.instances.all()
        for instance in instances:
            print(f"Instance ID: {instance.id}, Status: {instance.state['Name']}")

    def list_available_zones(self):
        response = self.ec2_client.describe_availability_zones()
        for zone in response['AvailabilityZones']:
            print(f"Zone: {zone['ZoneName']}, State: {zone['State']}")

    def start_instance(self, instance_id):
        self.ec2.instances.filter(InstanceIds=[instance_id]).start()
        # Update Condor Pool dynamically
        self.update_condor_pool()

    def stop_instance(self, instance_id):
        self.ec2.instances.filter(InstanceIds=[instance_id]).stop()
        # Update Condor Pool dynamically
        self.update_condor_pool()

    def create_instance(self):
        # Add logic to create a new instance
        # Update Condor Pool dynamically
        self.update_condor_pool()

    def reboot_instance(self, instance_id):
        self.ec2.instances.filter(InstanceIds=[instance_id]).reboot()

    def list_images(self):
        images = self.ec2.images.all()
        for image in images:
            print(f"Image ID: {image.id}, Name: {image.name}")

    def update_condor_pool(self):
        # Add logic to dynamically update Condor Pool
        print("Updating Condor Pool...")

    def list_available_regions(self):
        regions = self.ec2_client.describe_regions()
        for region in regions['Regions']:
            print(f"Region: {region['RegionName']}")

def main():
    print("      __          _______   __  __                                   \n")
    print("     /\ \        / / ____| |  \/  |                                  \n")
    print("    /  \ \  /\  / / (___   | \  / | __ _ _ __   __ _  __ _  ___ _ __ \n")
    print("   / /\ \ \/  \/ / \___ \  | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|\n")
    print("  / ____ \  /\  /  ____) | | |  | | (_| | | | | (_| | (_| |  __/ |   \n")
    print(" /_/    \_\/  \/  |_____/  |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   \n")
    print("                                                      __/ |          \n")
    print("   2020039091 Rocky Eo                               |___/   ")
    
    aws_manager = AWSResourceManager()

    while True:
        print("\n------------------------------------------------------------")
        print("1. list instances\t2. available zones")
        print("3. start instance\t4. available regions")
        print("5. stop instance\t6. create instance")
        print("7. reboot instance\t8. list images")
        print("99. quit")
        print("------------------------------------------------------------")

        choice = input("메뉴 선택: ")

        if choice == '1':
            aws_manager.list_instances()
        elif choice == '2':
            aws_manager.list_available_zones()
        elif choice == '3':
            instance_id = input("인스턴스 ID : ")
            aws_manager.start_instance(instance_id)
        elif choice == '4':
            aws_manager.list_available_regions()
        elif choice == '5':
            instance_id = input("인스턴스 ID : ")
            aws_manager.stop_instance(instance_id)
        elif choice == '6':
            aws_manager.create_instance()
        elif choice == '7':
            instance_id = input("인스턴스 ID : ")
            aws_manager.reboot_instance(instance_id)
        elif choice == '8':
            aws_manager.list_images()
        elif choice == '99':
            break
        else:
            print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()
