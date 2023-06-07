<a name="readme-top"></a>
_This repo is intended as a public preview. It will be re-created once the final version is complete._
# NetMRI Cisco OS Software Transfer
This script will automate the transfer of Cisco OS software upgrades to a device, or a group of devices, that are managed by NetMRI. It allows for network admins to schedule software transfers, and breaks free the poor soul in the NOC who gets stuck with the mundane task of transferring upgrades to thousands of devices.

This script is designed to run from the NetMRI UI, instead of externally. Doing this:
* Allows the NOC to access this script from your organization's existing NetMRI deployment.
* Allows for use of NetMRI's RBAC permissions on Script Level Execution.
* Allows for the ability to schedule the deployment.
* Allows this script to be deployed against Device Groups.
* Allows for this script to be used by Triggered Jobs.
* Allows for additional safety provided by AAA server command authorization.
* Allows for a limit on concurrent transfers initiated from the management network to your repo(s). (_NetMRI Settings > Advanced Settings > Configuration Management > Concurrent Jobs_)

<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <ul>
          <li><a href="#import-na_ciscoswtransferpy">Import na_ciscoswtransfer.py</a></li>
          <li><a href="#import-ciscodevicepy">Import CiscoDevice.py</a></li>
          <li><a href="#prepare-the-cisco-os-sw-hashes-csv">Cisco OS SW Hashes CSV</a></li>
          <ul>
            <li><a href="#prepare-the-cisco-os-sw-hashes-csv">Prepare the Cisco OS SW Hashes CSV</a></li>
            <li><a href="#import-the-cisco-os-sw-hashes-csv">Import the final Cisco OS SW Hashes CSV</a></li>
          </ul>
          <li><a href="#prepare-the-cisco-os-sw-regional-repos-csv">Cisco OS SW Regional Repos CSV</a></li>
          <ul>
            <li><a href="#prepare-the-cisco-os-sw-regional-repos-csv">Prepare the Cisco OS SW Regional Repos CSV</a></li>
            <li><a href="#import-the-cisco-os-sw-regional-repos-csv">Import the final Cisco OS SW Regional Repos CSV</a></li>
        </ul>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
    <li><a href="#useful-references">Useful References</a></li>
  </ol>
</details>

## Getting Started
Download the main branch .zip of this repo:  
<a href="https://github.com/ensmingera/na_ciscoswtransfer/archive/refs/heads/main.zip">https://github.com/ensmingera/na_ciscoswtransfer/archive/refs/heads/main.zip</a>

Or, clone it:
```sh
git clone https://github.com/ensmingera/na_ciscoswtransfer.git
```

## Prerequisites
* NetMRI version 7.5.0, or higher.
* NetMRI Sandbox version 7.5.0, or higher.
* CiscoDevice.py imported into NetMRI library.
* Software hash list imported to NetMRI.
* Regional repo list imported in to NetMRI.
* CLI credentials must have have sufficient AAA command authorization:
  * `show *`
  * `dir *`
  * `switchto *`
  * `changeto *`
  * `delete *`
  * `copy *`
  * `verify *`
  * `request software *`
  * `install *`
  * `configure terminal`
  * `boot *`
<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Installation
Installing this script is performed inside of the _Config Management_ Dashboard.  
Before you begin: Navigate to the _Config Management_ Dashboard, and then click on the _Job Management_ tab.

### Import _na_ciscoswtransfer.py_
1. Click on the _Scripts_ tab.
2. Click on the _Import_ button.
3. Click on the _Browse_ button.
4. Locate and select `na_ciscoswtransfer.py`.
5. Click on the _Import_ button.
6. You should now see the _Cisco OS Software Transfer_ script available in the Dashboard.  
![image](https://github.com/ensmingera/na_ciscoswtransfer/assets/33635167/c5b2752a-cf49-40d9-9462-ef04370acdc7)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Import _CiscoDevice.py_
1. Click on the _Library_ tab.
2. Click on the _Import_ button.
3. Click on the _Browse_ button.
4. Locate and select `CiscoDevice.py`.
5. Click on the _Import_ button.
6. You should now see _CiscoDevice_ installed in to the NetMRI libaries.  
![image](https://github.com/ensmingera/na_ciscoswtransfer/assets/33635167/154fa003-11b7-4e65-9ade-6e838f38109f)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prepare the Cisco OS SW Hashes CSV
The _Cisco OS SW Hashes_ list must be in this format:
| Filename | Size | MD5 | SHA512 |
|----------|------|-----|--------|
| `filename` | `size in bytes` | `MD5 hash` | `SHA-512 hash` |
1. Prepare instructions here...

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Import the Cisco OS SW Hashes CSV
1. Click on the _Lists_ tab.
2. Click on the _Import_ button.
3. Click on the _Choose File_ button.
4. Locate and select `cisco_os_sw_hashes.csv`.
5. Click on the _Import_ button.
6. You should now see _Cisco OS SW Hashes_ added to the NetMRI lists.  
![image](https://github.com/ensmingera/na_ciscoswtransfer/assets/33635167/949b11dc-c138-489c-a6b3-62f3aeeea020)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prepare the Cisco OS SW Regional Repos CSV
_If your organization implements AnyCast addressing for your repos, then you only need one row (per Network View). Or just specify an ad-hoc repo when deploying the job._  

The _Cisco OS SW Regional Repos_ list must be in this format:
| Region | Network View | Address |
|--------|--------------|---------|
| `Region` | `Network View` | `IP Address` |  

A repo is automatically selected based on the `repo_region` variable defined from the job UI, and from which _Network View_ in the device resides in NetMRI.  
The network view is retrieved using the `DeviceRemote` broker, by accessing the `DeviceRemote.virtual_network.VirtualNetworkName` attribute.  
1. Prepare instructions here...

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Import the Cisco OS SW Regional Repos CSV
1. Click on the _Lists_ tab.
2. Click on the _Import_ button.
3. Click on the _Choose File_ button.
4. Locate and select `cisco_os_sw_regional_repos.csv`.
5. Click on the _Import_ button.
6. You should now see _Cisco OS SW Regional Repos_ added to the NetMRI lists.  
![image](https://github.com/ensmingera/na_ciscoswtransfer/assets/33635167/3c5d0c04-41fa-4fbc-9242-567fb96036e3)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Usage
Usage ...

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Roadmap
Roadmap ...

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Contributing
Contributing ...

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Acknowledgments
Acks here

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Useful References
<a href="https://sec.cloudapps.cisco.com/security/center/resources/ios_nx_os_reference_guide">Cisco IOS and Cisco NX-OS Software Release Reference Guide</a>  
<a href="https://www.cisco.com/c/en/us/products/collateral/ios-nx-os-software/nx-os-software/guide_c07-658595.html">Cisco NX-OS Software Lifecycle Support Statement</a>  
<a href="https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-software-releases-110/13329-x-release.html">Guide to Cisco IOS Release Naming</a>  
<a href="https://www.cisco.com/c/en/us/td/docs/ios/fundamentals/command/reference/cf_book/cf_s1.html#wp1175770">Cisco IOS Configuration Fundamentals Command Reference (show file systems)</a>  
<a href="https://community.cisco.com/t5/networking-knowledge-base/cisco-ios-and-ios-xe-naming-convention-for-routing-platforms/ta-p/4520161">Cisco Community: Cisco IOS and IOS XE Naming Convention for Routing Platforms</a>  
<a href="https://community.cisco.com/t5/server-networking/what-does-nexus-1000v-version-number-say/m-p/2909762#M11124">Cisco Community: What does Nexus 1000v Version Number Say</a>  
<a href="https://www.cisco.com/c/en/us/td/docs/security/asa/upgrade/asa-upgrade/planning.html#ID-2152-0000008d">Cisco Secure Firewall ASA Upgrade Guide</a>  

<p align="right">(<a href="#readme-top">back to top</a>)</p>
