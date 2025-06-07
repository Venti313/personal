# Aeolus Setup Tools
https://bytedance.sg.larkoffice.com/docx/JZBsdH03jouDanxcAYzl3OIcgjf

## Definitions 
* Components refers to SCM, RDS, TCC, TCE.
* Services refers to the microservices in Aeolus. 

## What is Aeolus Setup Tools 
Aeolus Setup Tools is a collection of configurations and scripts used to ease the management and deployment of Aeolus 
in multiple regions.

The aim of this repository is as follows:
1. Allow proper documentation and record of configurations necessary for each release version of Aeolus
2. Provide a centralize repository to manage cross-cluster configuration. 
3. Provide a method to upgrade Aeolus Cluster for a specific region easily. 

Aeolus Setup Tools will support configuration and/or deployment of the following components:
1. RDS
2. TCC
3. TCE
4. MAAT


## How it works 
Configuration of components will be done via Bits Bytecycle. 
https://bits.bytedance.net/devops/4084924930/pipeline/list

* SCM - https://bits.bytedance.net/devops/4084924930/pipeline/detail/175327804162?enterType=all&devops_space_type=server_fe
* TCE - https://bits.bytedance.net/devops/4084924930/pipeline/detail/176980443650?enterType=all&devops_space_type=server_fe
* MAAT - https://bits.bytedance.net/devops/4084924930/pipeline/detail/176642438402?enterType=all&devops_space_type=server_fe

There is also a pipeline that upgrade all above components in a single process.
https://bits.bytedance.net/devops/4084924930/pipeline/detail/173807692290?enterType=all&devops_space_type=server_fe

Configuration of the pipeline is done in 3 tiers. 


