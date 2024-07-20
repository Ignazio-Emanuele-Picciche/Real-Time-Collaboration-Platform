# **_Real-Time Collaboration Platform - Architectures of Distributed Systems (23/24)_**

<!-- ## Index
1. [Project Description](#general-description-of-the-project)
    - [Project Objective](#project-objectives)
    - [Challenges](#challenges) -->

> [!NOTE] <br>
> You can find the complete documentation here: [english version](Real_Time_Collaboration_Platform_ENG.pdf) or [italian version](Real_Time_Collaboration_Platform_ITA.pdf)
>
> You can find the site here: http://34.154.59.47:8583/  **(DISABLED)**


### General description of the project
This project, made by Ignazio Emanuele Piccichè, Mattia Castiello and Michela Di Simone, has the purpose to develop a Real-Time Collaboration Platform that not only supports shared document editing but is also resilient to network partitions, thereby ensuring a reliable user experience.

#### Project Objectives
- Allow multiple users to edit the same document simultaneously, leveraging the use of WebSockets.
- Mantaining data consistency even in the presence of network partitions, using the _Conflict-free Replicated Data Types_ (CRDTs) technique.
- Handle network partitions in a way that ensures all changes are correctly integrated once the partition is resolved.
- Effectively notify the presence of users, informing who is currently connected to the shared document.

#### Challenges
To verify the robustness of the platform, targeted experiments were conducted, including:
- Simulating network partitions to test the system's ability to reconcile changes.
- Analyzing the impact of different conflict resolution strategies on the system's consistency and latency.

