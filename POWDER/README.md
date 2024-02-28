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
<br><img src=".\Profile-Screens\d430-info.png" width="300">
- VLAN Settings:
    - Create a Vlan: True
    - Shared Vlan Name: Appropriate Secret Shared Name for ourselves


#### Experiment 2 
Profile: [srslte-shvlan-oran](https://www.powderwireless.net/show-profile.php?profile=1bd95656-5b60-11eb-b1eb-e4434b2381fc)

**Parameters:**
- 1x Indoor OTA X310 (Role NodeB)
<br> acts as base transmission station connected to nodes and connecting to ORAN server
    <br> Shared Vlan IP Adress: unused address within the subnet of an existing shared vlan.
- 2x Indoor OTA Nuc with B210 (Role UE)
<br> Acts as UE connecting to eNB


            


## Setup
Start a new experiment with above mentioned profiles and following parameters

**ORAN Parameters:**  
1. Instantiate the Oran profile with default params and add a shared VLAN for link in the different exeriemnts.
<img src=".\Profile-Screens\ORAN Parameters.png"><br>
<img src=".\Profile-Screens\VLAN-Settings-ORAN.png"><br>

2. Finalize the Settings name and view topology to confirm if requirements are statisfied.
<img src=".\Profile-Screens\ORAN-Topology.png"><br>

3. Schedule and Instantiate the profile.
<img src=".\Profile-Screens\ORAN-Initializing.png"><br>


**srslte-shvlan-oran Parameters**<br>
**Indoor OTA Resources**
1. OTA X-310 with server for nodeB computing, add a shared VLAN IP within the same subnet
    <br><img src=".\Profile-Screens\X-310-Params.png">
2. 2x Indoor OTA Nuc with B210 for UE nodes, add a shared VLAN IP within the same subnet
    <br><img src=".\Profile-Screens\B-210-Params.png">
**VLAN Settings**
3. Add the shared VLAN Name from ORAN profile and allocate a IP address within the same subnet
    <br><img src=".\Profile-Screens\VLAN-Settings-srslte.png"><br>
4. Finalize the Settings name and view topology to confirm if requirements are statisfied.
    <br> <img src=".\Profile-Screens\srslte-Topology.png"><br>
5. Finally Scheduled and Instantiate the profile for use.
    <br> <img src=".\Profile-Screens\srslte-Initializing.png"><br>



## Problems
- Xiaochan submited the OTA permission for CPE900 Project, waiting for response.
- ~~DL/UL Frequency Parameters value.~~ Setting to 10MHz of C-Band Range:  3420 ==> 3445
- ~~DL RBG Mask.~~
- ~~UL PRB Mask.~~ Setting to empty for Auto-Config
Awaiting Radio Resources Reservation.

**Request to POWDER Team for Radio Devices Setup**

<img src=".\Profile-Screens\Screenshot 2024-02-21 231637.png" width="600" title="Warning">


