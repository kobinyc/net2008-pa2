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

        # If the element has an owner and the owner tag has text inside
        owner = element.find("owner")
        if owner != None and owner.text != None:
            self.owner = owner.text.strip()
        else:
            self.owner = ""

        # Creating the interfaces list
        self.interfaces = []
        for interface in element.findall("interface"):
            self.interfaces.append(interface.get("status", ""))

    # This function just counts the devices interfaces
    def count_interfaces(self):
        interface_counts = { 
                 "up": 0, 
                 "down": 0, 
                 "other": 0
                 }

        # For every status in the interfaces, increase the count for that status
        for status in self.interfaces:
            if status == "up":
                interface_counts["up"] += 1
            elif status == "down":
                interface_counts["down"] += 1
            else:
                interface_counts["other"] += 1

        return interface_counts