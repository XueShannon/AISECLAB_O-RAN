# AISECLAB Open Radio Access Network (O-RAN) Project
## Goal 
<details><summary>Midterm (End of March, 2024)</summary>
<p>
  Goal: Complete a simple whole Federated Learning Process
</p>
</details>
<details><summary>Final (End of May, 2024)</summary>
<p>
  1. data flow
  2. realistic problem (thinking)
</p>
</details>

## Meeting
- in-person (once a month)
- Zoom (Every Friday 2pm)
  
## O-RAN Architecture
Reference: [Understanding O-RAN: Architecture, Interfaces, Algorithms, Security, and Research Challenges](https://arxiv.org/pdf/2202.01032.pdf)

<img src="https://github.com/XueShannon/AISECLAB_O-RAN/blob/main/Architecture/O-RAN.jpg" height="400" width="550" >

<details>
<summary>Terms</summary>
  
* **A1**: Interface between non-RT RIC and Near-RT RIC to enable policy-driven guidance of Near-RT RIC applications/functions, and support AI/ML workflow.
* **Near-Real-Time RAN Intelligent Controller**: An O-RAN Network Function (NF) that enables near-real-time control and optimization of RAN elements and resources via fine-grained data collection and actions over E2 interface. It may include AI/ML (Artificial Intelligence / Machine Learning) workflow including model training, inference and updates. 
* **Non-Real-Time RAN Intelligent Controller**: A functionality within SMO that drives the content carried across the A1 interface.  It is comprised of the Non-RT RIC Framework and the Non-RT RIC Applications (rApps) whose services are defined below. 
* **Non-RT RIC Applications (rApps)**: Modular applications that leverage the functionality exposed via the Non-RT RIC Framework’s R1 interface to provide added value services relative to RAN operation, such as driving the A1 interface, recommending values and actions that may be subsequently applied over the O1/O2 interface and generating “enrichment information” for the use of other rApps.  The rApp functionality within the Non-RT RIC enables non-real-time control and optimization of RAN elements and resources and policy-based guidance to the applications/features in Near-RT RIC.  
* **O2**: Interface between SMO framework as specified in Clause 5.3.1 and the O-Cloud for supporting O-RAN virtual network functions. 
* **R1 Interface**: Interface between rApps and Non-RT RIC Framework via which R1 Services can be produced and consumed. 
* **SMO**: A Service Management and Orchestration framework.
* **xApp**: An application designed to run on the Near-RT RIC. Such an application is likely to consist of one or more microservices and at the point of on-boarding will identify which data it consumes and which data it provides. The application is independent of the Near-RT RIC and may be provided by any third party. The E2 enables a direct association between the xApp and the RAN functionality.
* **Y1**: An interface over which RAN analytics services are exposed by the Near-RT RIC to be consumed by Y1 consumers.

</details>

## Experimental wireless platforms and frameworks for O-RAN
### Platform
- [Arena](https://ece.northeastern.edu/wineslab/arena.php): container ready to use
- [Colosseum](https://www.northeastern.edu/colosseum/): container ready to use
- [AERPAW](https://aerpaw.org)
- [COSMOS](https://www.cosmos-lab.org)
- [POWDER](https://powderwireless.net): container ready to use --- [[use for now](https://github.com/XueShannon/AISECLAB_O-RAN/tree/main/POWDER)]
- [5GENESIS](https://5genesis.eu): building
### Framework
- [OpenRAN Gym](https://openrangym.com/other/publications)
- [Open AI Cellular](https://www.openaicellular.org)

### Open Source Protocol Stacks
- [srsRAN](https://www.srslte.com/srsran-project-update)
- [OpenAirInterface](https://openairinterface.org/news/o-ran-alliance-and-openairinterface-software-alliance-expand-cooperation-on-developing-open-software-for-the-ran/)
