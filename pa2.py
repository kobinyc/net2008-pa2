# Name: Kenechukwu Obi
# Student ID: 041301260

import json
import sys
import yaml
import xml.etree.ElementTree as ET

class Device:
    def __init__(self, element):
        self.id = element.get("id")
        self.role = element.get("role")
        self.os = element.get("os")

        """ If the element has an owner and the owner tag has text inside """
        owner = element.find("owner")
        if owner != None and owner.text != None:
            self.owner = owner.text.strip()
        else:
            self.owner = ""

        """ Creating the interfaces list """
        self.interfaces = []
        for interface in element.findall("interface"):
            self.interfaces.append(interface.get("status", ""))

    """ This function just counts the devices interfaces """
    def count_interfaces(self):
        interface_counts = { 
                 "up": 0, 
                 "down": 0, 
                 "other": 0
                 }

        """ For every status in the interfaces, increase the count for that status """
        for status in self.interfaces:
            if status == "up":
                interface_counts["up"] += 1
            elif status == "down":
                interface_counts["down"] += 1
            else:
                interface_counts["other"] += 1

        return interface_counts

" Helper function for checking if the operating system is outdated "
def os_outdated ( device_os, min_os ):

    if device_os == min_os:
        return False

    device_os_split = device_os.split(".")
    min_os_split = min_os.split(".")
    device_os_nums = []
    min_os_nums = []

    for num in device_os_split:
        device_os_nums.append(int(num))
    for num in min_os_split:
        min_os_nums.append(int(num))

    if len(device_os_nums) > len(min_os_nums):
        for x in range(0, len(device_os_nums) - len(min_os_nums)):
            min_os_nums.append(0)
    if len(min_os_nums) > len(device_os_nums):
        for x in range(0, len(min_os_nums) - len(device_os_nums)):
            device_os_nums.append(0)

    for num in range(0, len(device_os_nums)):
        if min_os_nums[num] > device_os_nums[num]:
            return True
        elif device_os_nums[num] > min_os_nums[num]:
            return False

    return False
    pass

""" This function is for auditing the xml file with the yaml file """
def write_report(xml_file, yaml_file):
    root = ET.parse(xml_file).getroot()

    with open(yaml_file, "r", encoding="utf-8") as file:
        policy = yaml.safe_load( file )
        if policy == None:
            policy = {}

    devices = []
    skipped_devices = 0

    for element in root.findall("device"):
        device = Device( element )

        if device.id == None or device.id == "":
            skipped_devices += 1
        else:
            devices.append( device )

    roles = {}
    interfaces = {
                 "up": 0,
                 "down": 0,
                 "other": 0
                 }

    """ Counting the roles """
    for device in devices:
        if device.role not in roles:
            roles[device.role] = 0

        roles[device.role] += 1

        for status, count in device.count_interfaces().items():
            interfaces[status] += count

    violations = []
    compliant = []

    """ Violations checks """
    for device in devices:
        device_violations = 0

        if "min_os" in policy:
            if device.role == None or not device.role in policy.get("min_os", {}):
                violations.append({
                "device" : device.id,
                "type": "unknown_role",
                "role": device.role
                })
                device_violations += 1

        if "require_owner" in policy:
            if device.owner == None or device.owner == "" and policy.get("require_owner", False):
                violations.append({
                "device" : device.id,
                "type": "missing_owner"
                })
                device_violations += 1
        
        if "max_down_interfaces" in policy:
            if device.count_interfaces()["down"] > policy.get("max_down_interfaces", False):
                violations.append({
                "device" : device.id,
                "type": "too_many_down",
                "down": device.count_interfaces()["down"]
                })
                device_violations += 1

        if "min_os" in policy and device.role in policy.get("min_os") and device.role != None:
            if os_outdated(device.os, policy.get("min_os", {}).get(device.role)):
                violations.append({
                "device": device.id,
                "type": "os_outdated",
                "required": policy.get("min_os", {}).get(device.role),
                "found": device.os
                })
                device_violations += 1
        
        if device_violations == 0:
            compliant.append( device.id )

    roles_dict = dict(roles)
    
    """ The report dictionary, this will be dumped into "audit.json" """
    report = {
            "site": root.get("site"),
            "total_devices": len(devices),
            "skipped_devices": skipped_devices,
            "roles": roles_dict,
            "interfaces": interfaces,
            "violations": violations,
            "compliant": sorted(compliant)
            }

    """ Dumping the report into a json """
    with open("audit.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    """ Audit message """
    print('"audit.json" has been created/overwritten.')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(" Missing arguments or too many arguments ")
        sys.exit(2)
    else:
        write_report(sys.argv[1], sys.argv[2])
        sys.exit(0)