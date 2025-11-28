# Scalable Disk Monitoring Solution for AWS

## Overview
This repository contains my proposed solution for a scalable disk monitoring system across multiple AWS accounts. The design leverages a hub-and-spoke model for secure access and uses a combination of AWS Systems Manager and a simple Lambda aggregator for data collection, avoiding the need for SSH keys and long-running agents.

## Architecture
Below is a high-level diagram of the solution:

![Architecture Diagram](./images/architecture-diagram.png)

*(Note: You will create this diagram and put it in an `/images` folder)*

### Key Components & Design Choices

1.  **Access Management (Solving "Ease of Access & Management")**
    *   **IAM Roles & Cross-Account Access:** A central "Monitoring" AWS account assumes IAM roles in spoke (workload) accounts. This is secure and doesn't require sharing credentials.
    *   **AWS Systems Manager (SSM):** SSM Agent is installed by default on many AMIs. It allows us to run commands on EC2 instances without SSH keys or bastion hosts, using IAM permissions.

2.  **Data Collection & Aggregation**
    *   **Discovery:** Use AWS Config or a simple Lambda function to discover all EC2 instances across enrolled accounts.
    *   **Metric Collection:** An Ansible playbook, run from the central account, uses the `aws_ssm` connection plugin to execute a disk usage command (e.g., `df -h`) on all discovered instances via SSM.
    *   **Aggregation:** The playbook parses the output and sends custom metrics to Amazon CloudWatch in the central account for a unified view.

3.  **Scalability**
    *   **Dynamic Inventory:** The Ansible playbook uses a custom dynamic inventory script that queries AWS for running EC2 instances, ensuring new instances are automatically included.
    *   **Serverless Components:** Using Lambda and CloudWatch means the solution scales automatically without managing servers.

## Repository Structure