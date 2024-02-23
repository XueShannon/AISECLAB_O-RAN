# O-RAN Experiment on POWDER
Description: All resources, setups, thoughts, and problems should be listed here

## Resources
[O-RAN on Powder](https://powderwireless.net/oran)

As suggested by POWDER we have to create two Experiments connected through shared vlan for ORAN-Server and UE nodes

#### Experiment 1 ORAN 
Profile [ORAN](https://www.powderwireless.net/show-profile.php?uuid=30d3e13c-f939-11ea-b1eb-e4434b2381fc)

- Parameters:
- Number of Nodes : 1
- H/w Type: d430
- VLAN Settings:
    - Connect to shared Vlan: True
    - Shared Vlan Name: Appropriate Secret Shared Name for ourselves


#### Experiment 2 
Profile: [srslte-shvlan-oran](https://www.powderwireless.net/show-profile.php?profile=1bd95656-5b60-11eb-b1eb-e4434b2381fc)

**Parameters:**
- 1x Indoor OTA X310 (Role NodeB)
<br> acts as base transmission stattion connected to nodes and connecting to ORAN server
    <br> Shared Vlan IP Adress: unused address within the subnet of an existing shared vlan.
- 2x Indoor OTA Nuc with B210 (Role UE)
<br> Acts as UE connecting to eNB

            


## Setup

## Problems
- Xiaochan submiited the OTA permission for CPE900 Project, waiting for response.
- DL/UL Frequency Parameters value.
- DL RBG Mask for eNB.
- UL PRB Mask

**Request to POWDER Team for Radio Devices Setup**

<img src=".\Profile-Screens\Screenshot 2024-02-21 231637.png" width="350" title="Warning">


