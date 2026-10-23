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

write_report(sys.argv[1], sys.argv[2])