###########################################################################
## Export of Script: Cisco OS Software Transfer
## Script-Level: 3
## Script-Category: Uncategorized
## Script-Language: Python
###########################################################################
# BEGIN-INTERNAL-SCRIPT-BLOCK
# Script:
# 	Cisco OS Software Transfer
#
# Script-Description:
# 	This script will automate the transfer of Cisco IOS, IOS-XE, NX-OS, or
#   ASA upgrades.
#
# END-INTERNAL-SCRIPT-BLOCK
# These are to just keep Pylance happy.
# Uncomment these to make your Pylance happy too.
# api_url = "http://netmri"
# http_username = "na_ciscoswtransfer"
# http_password = "foo"
# job_id = 7
# device_id = 31
# batch_id = 8
# hash_list = "Cisco OS SW Hashes"
# repo_region = "Region"
# override_automatic_repo_selection = "on"
# repo_host_override = "IP Address"
# repo_directory_path = "/pub/cisco/ios/"
# max_retries = "0"
# attempt_storage_space_reclaim_if_full = "on"
# clean_old_images = "on"
# dry_run = "on"
# enable_debug = "on"
#------------------------------------------------------------------------------
# NetMRI Cisco OS Software Transfer
# na_ciscoswtransfer.py
#
# Austin Ensminger
# Copyright (c) 2023 Infoblox, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# DESCRIPTION:
#   This script will automate the transfer of Cisco OS software upgrades to a
#   device managed by NetMRI.
#
#   Supported Cisco Platforms:
#       - IOS
#       - IOS-XE (no SD-WAN)
#       - NX-OS 5K/6K/7K [Version 4.0(1), or higher]
#       - NX-OS 3K/9K [in NX-OS mode]
#       - Adaptive Security Appliance (ASA) 5500-X Series [Ver. 9, or higher]
#
# PREQUISITES:
#   1. NetMRI version 7.5+
#   2. NetMRI Sandbox version 7.5+
#   3. CiscoDevice.py imported into NetMRI library.
#   4. Software hash list imported to NetMRI.
#   5. Regional repo list imported in to NetMRI.
#      (It is possible to just select "Override Automatic Repo Selection", and
#       then provide an ad-hoc repo)
#   6. CLI credentials must have have sufficient AAA command authorization:
#       - show *
#       - dir *
#       - changeto *
#       - switchto *
#       - delete *
#       - copy *
#       - verify *
#       - request software *
#       - configure terminal
#       - write memory
#       - NOTE:... what else?
#
# NOTES:
#   1. The software hash list must only contain ONE filename, per-platform,
#      to match the target upgrade file. (NX-OS kickstart is exception)
#   2. This script transfers only to the default file system for the device. It
#      will warn you if the current running image is not on the default file
#      system, but it will transfer the target upgrade to the default fs.
#   3. It's recommended to have 'ip tcp path-mtu-discovery' configured on the
#      device.
#   4. If the repos all have the same directory path, you can change the
#      default value for 'repo_directory_path' in the CCS script section below.
#
# LIMITATIONS:
#   1. This does not automate the actual upgrade process (yet!)
#   2. This does not check if the target upgrade image is actually a downgrade.
#   3. This does not transfer an ASDM image to ASA.
#   4. This does not transfer ROMMON upgrades.
#   5. Since this script does not delete the current running image during
#      space reclamation, it will fail for devices that can only store one
#      image on the fs at a time (e.g: old 3560, 2960, etc.)
#   6. If the current running image was renamed on the device, and then booted
#      to the renamed image, then this script will continue on as if the device
#      needs the upgrade.
#      e.g: "c3560cx-universalk9-mz.152-7.E7.bin" was copied, renamed to 
#      "latest_ios.bin", boot set with "boot system flash:/latest_ios.bin",
#      then booted to it.
#   7. This copies using 'http' protocol (Other protocols may come later)
#   8. This script assumes the HTTP client source interface is in a global VRF,
#      and the repo is accessible via the global VRF. (May possibly allow VRF
#      definition for Nexus or nameif for ASA, but IOS requires config change)
#   9. If you are attempting to transfer a NX-OS upgrade that is version
#      7.0(3)I2(1) or higher, and the Nexus is currently running a lower
#      version, then this script will fail.
#      Starting with version 7.0(3)I2(1) the system and kickstart images were
#      combined.
#      You need to manually transfer and follow specific upgrade path
#      (otherwise you'll brick your Nexus and have to RMA it). Once the
#      Nexus is upgraded to 7.0(3)I2(1) or higher, then this script will be
#      able to transfer future upgrades to it.
#   10. This script checks if the target upgrade already exists in the default
#       file system on the device, but it does not check if it is also on stack
#       members, in slave-bootflash, etc..
#   11. This script does not copy over to an ASA failover host. It is assumed
#       that failover hosts have been discovered & managed by NetMRI.
#       Make sure you run jobs against all failover hosts, as they are
#       considered to be independently managed devices.
#
# USEFUL REFERENCES:
# https://sec.cloudapps.cisco.com/security/center/resources/ios_nx_os_reference_guide
# https://www.cisco.com/c/en/us/products/collateral/ios-nx-os-software/nx-os-software/guide_c07-658595.html
# https://www.cisco.com/c/en/us/td/docs/ios/fundamentals/command/reference/cf_book/cf_s1.html#wp1175770
# https://community.cisco.com/t5/networking-knowledge-base/cisco-ios-and-ios-xe-naming-convention-for-routing-platforms/ta-p/4520161
# https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-software-releases-110/13329-x-release.html
# https://community.cisco.com/t5/server-networking/what-does-nexus-1000v-version-number-say/m-p/2909762#M11124
# https://www.cisco.com/c/en/us/td/docs/security/asa/upgrade/asa-upgrade/planning.html#ID-2152-0000008d
#------------------------------------------------------------------------------
import re
from infoblox_netmri.easy import NetMRIEasy
from CiscoDevice import CiscoDevice
#------------------------------------------------------------------------------
# BEGIN-SCRIPT-BLOCK
#
#   Script-Filter:
#       $Vendor eq "Cisco"
#       and $sysDescr like /IOS|NX-OS|Adaptive Security Appliance/
#       and $Type in ['Router', 'Switch-Router', 'Switch', 'Firewall']
#
#   Script-Timeout: 43200
#
#   Script-Variables:
#       $hash_list string "Cisco OS SW Hashes"
#       $repo_region string "Region"
#       $override_automatic_repo_selection boolean
#       $repo_host_override string "IP Address" ipaddr
#       $repo_directory_path string "Directory path"
#       $max_retries int 3 number
#       $attempt_storage_space_reclaim_if_full boolean
#       $clean_old_images boolean
#       $dry_run boolean
#       $enable_debug boolean
#
# END-SCRIPT-BLOCK
#------------------------------------------------------------------------------
def get_list_id(nmri, list_name):
    """Search for a NetMRI list by name and return the ID
    
    Args:
        - nmri: NetMRIEasy class reference.
        - list_name: String of the list name to find.

    Returns:
        The integer ID of the list.
    
    Raises:
        Exception if nothing was found.
    """
    broker = nmri.broker("ConfigList")
    response = broker.index()
    for item in response:
        if list_name == item.name:
            return item.id
    # No match, raise exception.
    err = f'List "{list_name}" does not exist in this NetMRI.'
    nmri.log_message("error", f"- {err}")
    raise Exception(err)


def get_upgrade_file_info(nmri, device, list_id, kickstart=False):
    """Get the filename, size, and hashes of the target upgrade file

    Args:
        - nmri: NetMRIEasy class reference.
        - device: CiscoDevice class reference.
        - list_id: ID integer of the NetMRI list to search.
        - kickstart: True returns NX-OS kickstart image. Default is false.

    Returns:
        Dictionary of the first match, from the hash list.

    Raises:
        Exception if nothing was found.
    """
    platform = device.platform
    broker = nmri.broker("ConfigList")
    response = broker.search_rows(id=list_id)
    for item in response['list_rows']:
        # 2023.05.25 - aensminger - Add generator, so we match
        # "c800-" to c800-univeralk9-mz.xxx-x.xx.bin,
        # instead of c800 getting matched with c8000aep-universalk9...
        if (device.os != "ASA" and
            any(item['Filename'].startswith(plat)
                for plat in (platform + '-', platform + '_', platform + '.'))):
            # Remove commas and store size as integer.
            item['Size'] = int(item['Size'].replace(",", ""))

            # Return the kickstart image for NX-OS
            if kickstart and "kickstart" in item['Filename']:
                return item

            # Return the match
            if not kickstart:
                return item

        # ASA does not have delimiter between the platform and version.
        # So we have to put it's own handling here.
        if device.os == "ASA" and item['Filename'].startswith(platform):
            # Remove commas and store size as integer.
            item['Size'] = int(item['Size'].replace(",", ""))

            # Return appropriate item for ASA.
            # 5506-X, 5508-X, 5516-X.
            if device.asa_is_lfbff and "lfbff" in item['Filename']:
                return item

            # 5512-X, 5515-X, 5525-X, 5545-X, 5555-X, 5585-X, ASAv
            if device.asa_is_smp and "smp" in item['Filename']:
                return item

            # Legacy ASA.
            return item

    # No match, raise exception.
    err = f'Unable to find target image for platform "{platform}"'
    nmri.log_message("error", f"- {err}")
    raise Exception(err)


def validate_fs_space_available(nmri, size, fs_dict):
    """Validate file system(s) free space for upgrade file
    
    Args:
        - nmri: NetMRIEasy class reference
        - size: Integer of size required in bytes.
        - fs_dict: The CiscoDevice.system_fs_info dictionary.

    Returns:
        dict: Dictionary with the following keys:
        - 'pass' (bool): True if validation succeeds, False if it failed.
        - 'fs' (list): List of file systems that failed.
    """
    fs_validation_failed = {"pass": True, "fs": []}
    for fs_item in fs_dict:
        if (int(size) > int(fs_dict[fs_item]['free'])):
            space_exceeded = (int(size) - int(fs_dict[fs_item]['free']))
            nmri.log_message("warn",
                             f"{' '*2}[FAIL] {fs_dict[fs_item]['fs']}:"
                             " Target upgrade image exceeds the available"
                             f" space by {space_exceeded} bytes.")
            fs_validation_failed['fs'].append(fs_dict[fs_item]['fs'])
        else:
            space_free = (int(fs_dict[fs_item]['free']) - int(size))
            nmri.log_message("info",
                             f"{' '*2}[PASS] {fs_dict[fs_item]['fs']}:"
                             f" {space_free} bytes free after transfer.")
    if fs_validation_failed['fs']:
        fs_validation_failed['pass'] = False
    return fs_validation_failed


def get_repo_info(list_id, region, network_view):
    """Reads Cisco OS SW Regional Repos and returns the repo information
    
    Args:
        - list_id: The list ID of the Cisco OS SW Regional Repos list.
        - region: The region from the Cisco OS SW Regional Repos list.
        - network_view: Network View. Passed from DeviceRemote.network_name

    Returns:
        str: The address of the repo which network view and region matches.

    Raises:
        Exception if no repo found.
    """
    broker = nmri.broker("ConfigList")
    response = broker.search_rows(id=list_id)
    for item in response['list_rows']:
        if item['Region'] == region and item['Network View'] == network_view:
            nmri.log_message("info",
                             f"{' '*2}Selected repo: {item['Address']}")
            return item['Address']
    # No match, raise exception.
    err = f'Unable to find repo for region "{region}", view {network_view}'
    nmri.log_message("error", f"{' '*2}{err}")
    raise Exception(err)


def remove_old_images(nmri, device, fs_list):
    """Deletes all old images, except the current running image,
    on the specified file system

    NOTE: The running image filename from "show version" output gets truncated
    on some Cisco devices. This func uses .startswith() to avoid that problem.

    Args:
        - nmri: NetMRIEasy class reference.
        - device: CiscoDevice class reference.        
        - fs: List of file system(s) to delete from.
    """
    # Initialize list for found files to delete.
    image_list = []

    if device.iosxe_boot_mode == "INSTALL":
        # Similiar to 'install remove inactive', except there's no 30-minute
        # delay for command output, and we don't remove .conf files.
        for fs_name in fs_list:
            nmri.log_message(
                "info",
                f"{' '*2}Enumerating old images/inactive packages from"
                f" {fs_name}:"
            )
            # Prepare command
            cmd = (
                f"dir {fs_name}:/{device.platform}* | include \.bin|\.pkg"
            )
            # Send it and parse output
            raw_output = device.dis.send_command(cmd)
            for line in raw_output.splitlines():
                # Group 1 is the filename: cat9k-rpboot.16.12.03a.SPA.pkg
                # Group 2 is the build: 16.12.03a
                match = re.search(
                    fr'.*(?<=\s)({device.platform}\S+\.(\d+\.\d+\.\d+[a-zA-Z]?'
                    ')\..*)', line
                )
                if match:
                    file = match.group(1)
                    build = match.group(2)
                    ftype_map = {
                        ".pkg": "inactive package",
                        ".bin": "old image"
                    }
                    ftype = ftype_map.get(file[file.rfind("."):], "unknown")
                    # Don't include the current running package
                    if build != device.iosxe_build:
                        nmri.log_message(
                            "info",
                            f"{' '*4}Found {ftype}: {fs_name}:/{file}"
                        )
                        image_list.append(file)

            # Delete old images from the list
            if len(image_list) > 0:
                nmri.log_message(
                    "info",
                    f"{' '*6}Deleting {len(image_list)} old images/"
                    f"inactive packages from {fs_name}:"
                )
                for i, image in enumerate(image_list, start=1):
                    nmri.log_message(
                        "info",
                        f"{' '*8}({i}/{len(image_list)})"
                        f" Deleting {fs_name}:/{image}"
                    )
                    cmd = f"delete /force /recursive {fs_name}:/{image}"
                    if dry_run:
                        nmri.log_message("info", f"dry-run cmd: {cmd}")
                    else:
                        device.dis.send_command(cmd)
            else:
                nmri.log_message(
                    "info", f"{' '*4}No old images/inactive packages"
                    f" found in {fs_name}:"
                )
        return

    if device.os == "NX-OS":
        if device.nxos_aci_mode == True:
            raise Exception("Nexus in ACI mode is not supported.")
        
        nmri.log_message("info", f"{' '*2}Enumerating old images from"
                         f" {device.system_fs}")
        
        # Search for kickstart images, if this NX-OS has kickstart.
        if device.nxos_kickstart_image is not None:
            nmri.log_message("info", f"{' '*2}Enumerating old kickstart images"
                             f" from {device.system_fs}:")
            cmd = (f"dir {device.system_fs}: |"
                   f"include {device.platform}.*\.bin$ | include kickstart")
            raw_output = device.dis.send_command(cmd)
            for line in raw_output.splitlines():
                match = re.search(r'(?:.*\/|.*(?<=\s)(\S+))', line)
                if match:
                    file = match.group(1)
                    if not file.startswith(device.nxos_kickstart_image):
                        nmri.log_message("info", f"{' '*4}Found old kickstart"
                                        f" image: {device.system_fs}:/{file}")
                        image_list.append(file)

        # Search for old images that are not kickstart.
        cmd = (f"dir {device.system_fs}: | include {device.platform}.*\.bin$ |"
               " exclude kickstart")
        raw_output = device.dis.send_command(cmd)
        for line in raw_output.splitlines():
            match = re.search(r'(?:.*\/|.*(?<=\s)(\S+))', line)
            if match:
                file = match.group(1)
                if not file.startswith(device.current_system_image):
                    nmri.log_message("info", f"{' '*4}Found old image:"
                                    f" {device.system_fs}:/{file}")
                    image_list.append(file)
        # Delete old images from the list
        if len(image_list) > 0:
            nmri.log_message("info",
                             f"{' '*6} Deleting {len(image_list)}"
                             f" old images from {device.system_fs}:")
            for i, image in enumerate(image_list, start=1):
                nmri.log_message("info", 
                                 f"{' '*8}({i}/{len(image_list)})"
                                 f" Deleting {device.system_fs}:/{image}")
                cmd = f"delete {device.system_fs}:/{image} no-prompt"
                if dry_run:
                    nmri.log_message("info", f"dry-run cmd: {cmd}")
                else:
                    device.dis.send_command(cmd)
        else:
            nmri.log_message("info",
                             f"{' '*4} No old images found in"
                             f" {device.system_fs}:")
        return

    # ASA/IOS/IOS-XE device
    if device.os == "ASA":
        # ASA does not allow you to pipe 'dir' output.
        cmdpfx = "show"
        delargs = "/noconfirm /recursive"
    else:
        # IOS/IOS-XE/NX-OS allow dir to be piped.
        cmdpfx = "dir"
        delargs = "/force /recursive"
    
    for fs_name in fs_list:
        nmri.log_message("info",
                         f"{' '*2} Enumerating old images from {fs_name}:")
        cmd = (f"{cmdpfx} {fs_name}: | include {device.platform}"
               ".*(\.SPA$|\.bin$)") #make sure we only match .SPA or .bin
        raw_output = device.dis.send_command(cmd)
        for line in raw_output.splitlines():
            match = re.search(fr'.*(?<=\s)({device.platform}\S+)',line)
            if match:
                file = match.group(1)
                # Don't include the current running image
                if not file.startswith(device.current_system_image):
                    nmri.log_message("info",
                                     f"{' '*4} Found old image:"
                                     f"{fs_name}:/{file}")
                    image_list.append(file)
        # Delete old images from the list
        if len(image_list) > 0:
            nmri.log_message("info", f"{' '*6}Deleting {len(image_list)}"
                            f" old images from {fs_name}:")
            for i, image in enumerate(image_list, start=1):
                nmri.log_message("info",
                                 f"{' '*8}({i}/{len(image_list)})"
                                 f" Deleting {fs_name}:/{image}"
                )
                cmd = f"delete {delargs} {fs_name}:/{image}"
                if dry_run:
                    nmri.log_message("info", f"dry-run cmd: {cmd}")
                else:
                    device.dis.send_command(cmd)
        else:
            nmri.log_message("info",
                             f"{' '*4} No old images found in {fs_name}:")
    return


def transfer_upgrade_image(nmri, repo_addr, image, device):
    """Copies the target upgrade image from the regional repo to the device.
    
    Transfer protocol is http.   
    
    Args:
        - nmri: NetMRIEasy class reference.
        - repo_addr: The repo address.
        - image: The dict from upgrade_file_info().
        - device: CiscoDevice class reference.

    Raises:
        Exception if failure.
        - Exception.args[1] will contain the error code in hex:
            - 0x00 : General error
            - 0x3f : Read error (e.g: broken pipe)
            - 0x7f : Host unresponsive, or remote file not found.
            - 0xbf : Incomplete transfer
            - 0xff : API error
    """
    proto="http" # TODO: Make this optional argument

    # Set up the copy command.
    if device.os == "ASA":
        # ASA does not handle broken pipe. It will save what was
        # downloaded so far, not give any error, and appear to succeed.
        # It'll get sorted out when get_file_size_info() method is called.
        copy_cmd = (f"copy /noconfirm {proto}://{repo_addr}"
                    f"{repo_directory_path}/{image['Filename']}"
                    f" {device.system_fs}:/{image['Filename']}")

    elif device.os == "NX-OS":
        # Nexus uses cURL (curl -O -f {host}).
        copy_cmd = (f"copy {proto}://{repo_addr}{repo_directory_path}/"
                    f"{image['Filename']} {device.system_fs}"
                    f":/{image['Filename']} vrf default")

    else:
        # This is for IOS/IOS-XE:
        copy_cmd = (f"copy {proto}://{repo_addr}{repo_directory_path}/"
                    f"{image['Filename']} {device.system_fs}"
                    f":/{image['Filename']}\r\r\r")
                    #Append carriage return to account addl. prompts.
    
    # Start transfer
    nmri.log_message("info",
                     f"{' '*2}Starting transfer. Waiting for return prompt"
                     " (See Session Log tab for progress) ...")
    ex = None
    try:
        if dry_run:
            raw_output = "\nDRY RUN"
            nmri.log_message("info", f"dry_run send_async_command: {copy_cmd}")
            return
        else:
            # NOTE: Timeout doesn't even work? regex seems borked too..
            # USE BLANK REGEX FOR POS ARG 3, OTHERWISE YOU WILL SEE RED..
            raw_output = device.dis.send_async_command(copy_cmd, 15300, "")
        raw_output = raw_output.splitlines()
        xfr_status = raw_output[-1]
        if enable_debug:
            nmri.log_message("debug", f"raw_output={raw_output}\n"
                             f"xfr_status={xfr_status}")
    except Exception as ccs_error:
        # Handle ccs error ourselves.
        ccs_err_info = ccs_error.args[0]
        # IOS/IOS-XE/ASA/NX-OS 0x7f Host unresponsive, or file not found.
        if ("Error opening" in ccs_err_info['message'] #IOS/IOS-XE/ASA
                or "404 Not Found" in ccs_err_info['message']): #NX-OS
            xfr_status = "%(ERR_OPEN)"
        # ASA partial transfer (broken pipe)
        elif "Signature not valid" in ccs_err_info['message']:
            xfr_status = "%(Error reading)"
        # send_async_command returns sometimes returns blank output in cases
        # where xfer completes in under 30 seconds.
        # Not sure how to handle this yet.
        else:
            xfr_status = "%(API_ERR)"
        if enable_debug:
            nmri.log_message("debug", f"ccs_err_info: {ccs_err_info}")

    nmri.log_message("info", f"{' '*2}Prompt returned. Validating status ...")

    # IOS/IOS-XE/ASA shows "%" in line with error.
    if device.os != "NX-OS" and "%" in xfr_status:
        match = re.search(r'%(?:.*\((.*)\))', xfr_status)
        last_status = match.group(1) if match else "Unknown"
        if "ERR_OPEN" in last_status:
            ex = Exception(f"Host unresponsive or file not found")
            ex.args += (0x7f,)
        elif "API_ERR" in last_status:
            ex = Exception("API error")
            ex.args += (0xff,)
        elif "Broken pipe" in last_status:
            ex = Exception("Broken pipe")
            ex.args += (0x3f,)
        else:
            # There are instances where we get jacked up return, and we can't
            # see last_status.... If "Error reading", then more than likely it
            # is broken pipe. So send broken pipe code and retry.
            if "Error reading" in xfr_status:
                ex = Exception("Transfer read error")
                ex.args += (0x3f,)
            # Or some other shenanigans we can't handle, yet.
            else:
                ex = Exception(f"General error [{last_status}]")
                ex.args += (0x00,)

    # NX-OS uses cURL, so we get to use cURL error codes (man 3 libcurl-errors)
    elif device.os == "NX-OS":
        for line in raw_output:
            if "Copy complete" in line:
                last_status = 0 #CURLE_OK
            elif "curl:" in line:
                match = re.search(r'(?:curl:\s+)\((\d+)\)', line)
                if match:
                    last_status = int(match.group(1))

        # Was code anything except CURLE_OK?
        if last_status > 0:
            #CURLE_COULDNT_RESOLVE_HOST
            if last_status == 6:
                ex = Exception("Host unresolvable")
                ex.args += (0x70,)
            #CURLE_COULDNT_CONNECT
            if last_status == 7:
                ex = Exception("Host unresponsive")
                ex.args += (0x7f,)
            #CURLE_PARTIAL_FILE
            elif last_status == 18:
                ex = Exception("Broken pipe")
                ex.args += (0x3f,)
            # CURLE_HTTP_RETURNED_ERROR
            elif last_status == 22:
                ex = Exception("File not found")
                ex.args += (0x7f,)
            else:
            # Something else. Send code back.
            # If it needs to be handled, then handle it.
                ex = Exception(f"cURL error: {last_status}")
                ex.args += (0x00,)

    # There was no error (that we could see).
    # Validate transfer.
    else:
        sz = device.get_file_size_info(device.system_fs, image['Filename'])
        # If there is a file, then get the file size. Otherwise, -1.
        if sz[0] and sz[1] >= 0:
            xfr_sz = sz[1]
        else:
            xfr_sz = -1

        # Check if bytes match expected value.
        if xfr_sz != image['Size']:
            ex = Exception("Incomplete transfer")
            ex.args += (0xbf,)

    # Pass or fail?
    if ex:
        nmri.log_message("info", f"{' '*2}[FAIL] Reason:"
                         f" [{hex(ex.args[1])} - {ex.args[0]}]")
        raise ex
    else:
        nmri.log_message("info", f"{' '*2}[PASS] Transfer completed")
        return   


def verify_image_integrity(f_info, device):
    """Verifies the integrity of an image file.
    
    NOTE: If the platform/version can support SHA-512 verification, and there
    is a SHA-512 hash in the hast list, then SHA-512 will be prioritized
    over MD5.

    Args:
        - f_info (dict): See upgrade_file_info() documentation.
        - device (cls): CiscoDevice reference.

    Returns:
        - bool: True if succeed. False if failed.
    """
    nmri.log_message("info", f"{' '*2}Starting image integrity verification."
                     " Waiting for return prompt (See Session Log tab for"
                     " progress) ...")

    # TODO: Seriously cannot tell which platforms/versions support sha512.
    # IOS 15.2(7) has it, but 15.7(3) doesn't?

    # Set the algo used for the verification command
    # if f_info['SHA512']:
    #     h_algo = "sha512"
    # elif f_info['MD5']:
    #     h_algo = "md5"
    # else:
    #     raise Exception("Hash algo and value not found")
    if f_info['MD5']:
        h_algo = 'md5'
        expected_hash = f_info['MD5']
    else:
        raise Exception("MD5 hash not in the list")

    # Pre-set the flag for if the version supports sha512.
    #sha512able = False

    if device.os == "ASA":
    # All ASA 9.x supports sha-512
        #h_algo = "sha-512" if "sha512" in h_algo else h_algo
        #expected_hash = f_info['SHA512']
        cmd = (
            f"verify /{h_algo} {device.system_fs}:/{f_info['Filename']}"
            f" {expected_hash}"
        )
    if device.os == "NX-OS":
    # Which NX-OS supports sha512?
    # NX-OS 6.0(2)A7(2) does not have sha512 verify.
    # NX-OS 6.0(2)A8(11b) has sha256 but not sha512.
    # NX-OS 7.0(3)I7(6) has it.
    # NX-OS 9.3(11) has it
    # So just check if higher than major version 7
        # NOTE: NX-OS does not verify image. Just returns hash of the file.
        # match = re.search(r'(\d+)\.(\d+)\((\d+)(\w+)?\)(.*)', device.version)
        # if match:
        #     v_maj = int(match.group(1)) # Major release
        #     v_min = int(match.group(2)) # Minor release
        #     v_mnt = int(match.group(3)) # Maintenance release
        #     v_rbld = match.group(4)     # Rebuild

        #     if ((v_maj == 7 and ((v_min == 0 and v_mnt >= 3) or (v_min > 0)))
        #             or (v_maj > 7)):
        #         sha512able = True

        # if sha512able and f_info['SHA512']:
        #     expected_hash = f_info['SHA512']
        #     h_algo = "sha512sum" if "sha512" in h_algo else h_algo
        # else:
        #     expected_hash = f_info['MD5']
        #     h_algo = "md5"
        cmd = f"show file {device.system_fs}:/{f_info['Filename']} {h_algo}"

    if device.os == "IOS-XE":
    # Which IOS-XE supports sha512?
    # Version 03.09.00.E does not have it
    # Version 03.11.02.E has it
    # Version 16.3.7 does not have it.
    # Version 16.5.1b has it. (Everest. idk if 16.4 has it.)
    # So check if higher than 03.11.02 or 16.5.1.
        # match = re.search(r'(\d+)\.(\d+)\.(\d+)\.?(\S+)?', device.version)
        # if match:
        #     v_maj = int(match.group(1))     # Major version
        #     v_rel = int(match.group(2))     # Release version
        #     v_rbld = int(match.group(3))    # Rebuild
        #     v_spcrel = match.group(4)       # Special release

        #     # IOS-XE 3.x
        #     if v_maj == 3:
        #         if (v_rel == 11 and v_rbld == 2) or (v_rel >= 11):
        #             h_algo = "sha512"

        #     # IOS-XE "Peaks"
        #     if v_maj > 16:
        #         sha512able = True
        #     if v_maj == 16:
        #         if ((v_rel == 5 and v_rbld == 1 and v_spcrel == "b")
        #                 or (v_rel >= 5 and v_rbld > 1)):
        #             sha512able = True

        # if sha512able and f_info['SHA512']:
        #     expected_hash = f_info['SHA512']
        #     h_algo = "sha512" if "sha512" in h_algo else h_algo
        # else:
        #     expected_hash = f_info['MD5']
        #     h_algo = "md5"
        cmd = (
            f"verify /{h_algo} {device.system_fs}:/{f_info['Filename']}"
            f" {expected_hash}"
        )
    if device.os == "IOS":
    # NOTE: Same for IOS.. Some monolithic IOS support SHA-512, but some don't.
    # How to tell which ones support SHA-512?? Can't find anywhere in Cisco
    # release notes.
    # Version 15.2(4)M8 does not have it.
    # Version 15.2(7)E has it
    # So check if higher than Train 15.2, Throttle 7 ...
        # if device.version.startswith("15"):
        #     match = re.search(r'([0-9.]+)\((\d+)\)', device.version)
        #     train = float(match.group(1))
        #     throttle = int(match.group(2))
        #     if (train == 15.2 and throttle >= 7) or train > 15.2:
        #         sha512able = True

        # if sha512able and f_info['SHA512']:
        #     expected_hash = f_info['SHA512']
        #     h_algo = "sha512" if "sha512" in h_algo else h_algo
        # else:
        #     expected_hash = f_info['MD5']
        #     h_algo = "md5"
        cmd = (
            f"verify /{h_algo} {device.system_fs}:/{f_info['Filename']}"
            f" {expected_hash}"
        )

    # Verify the image
    result = False
    if dry_run:
        raw_output = "\nDRY RUN"
        nmri.log_message("info", f"dry-run send_command: {cmd}")
        return True
    else:
        raw_output = device.dis.send_command(cmd)
        nmri.log_message("info",
                         f"{' '*2}Prompt returned. Validating status ...")
        if enable_debug:
            nmri.log_message("debug", f"return: {repr(raw_output)}")
        raw_output = raw_output.splitlines()
        if device.os == "NX-OS":
        # NX-OS returns one line with the sha512sum/md5sum result
            result = True if raw_output[-1] == expected_hash else False
        else:
        # IOS, IOS-XE, and ASA returns "Verified" or "%Error verifying"
            for line in raw_output:
                if "Verified" in line:
                    result = True
    if result:
        nmri.log_message("info",
                         f"{' '*2}[PASS] Integrity verification OK")
    else:
        nmri.log_message("info",
                         f"{' '*2}[FAIL] Integrity verification failed")
    return result


def xfer_handler(nmri, repo_addr, file_info, device, xfr_retry=0):
    """Handler loop for image transfers.

    Args:
        - nmri (cls): The NetMRIEasy class reference.
        - repo_addr (str): The repo address.
        - file_info (dict): The dict from upgrade_file_info().
        - device (cls): CiscoDevice class reference.
        - xfr_retry (int): Number of retry attempts. (Default: 0)

    Returns:
        None if loop completed with no errors.

    Raises:
        Exception if failure.
    """
    # Pre-set the failure reason.
    reason = "Unknown"
    # Single pass, or not?
    single_pass = True if xfr_retry < 1 else False
    xfr_retry = 0 if xfr_retry < 1 else xfr_retry
    # Begin loop
    while xfr_retry >= 0:
        try:
            transfer_upgrade_image(nmri, repo_addr, file_info, device)
            nmri.log_message("notif", "Upgrade image transfer complete.")
            # Returned ok, so we're good.
            nmri.log_message("notif",
                             "Starting integrity check of upgrade image ...")
            img_hash_pass = verify_image_integrity(file_info, device)
            # If integrity check passed, break from the loop. We're complete.
            if img_hash_pass:
                nmri.log_message("notif",
                                 "Upgrade image integrity check passed.")
                break
            else:
            # Transfer completed, but integrity check failed.
            # Raise error code, so we can retry.
                nmri.log_message("warn",
                                 "Upgrade image integrity check failed.")
                ex = Exception("Integrity check failed.")
                ex.args += (0xdf,)
                raise ex
        except Exception as xfr_exp:
            # NOTE: Set xfr_retry to -1, to break the loop early.
            # Don't do break, otherwise we'll stay in the loop.
            if len(xfr_exp.args) > 1:
                # These are the conditions that we allow xfer retry:
                # - 0x00: General error
                # - 0x3f: Broken pipe
                # - 0xbf: Incomplete transfer
                # - 0xdf: Integrity check failed
                if (xfr_exp.args[1] == 0x00
                        or xfr_exp.args[1] == 0x3f
                        or xfr_exp.args[1] == 0xbf
                        or xfr_exp.args[1] == 0xdf): 
                    xfr_retry -= 1
                    if xfr_retry >= 0:
                        nmri.log_message(
                            "notif",
                            f"({max_retries - xfr_retry}/"
                            f"{max_retries})"
                            " Retrying transfer of upgrade image ..."
                        )
                        # Delete the partial file.
                        if device.os == "NX-OS":
                            device.dis.send_command(
                                f"delete {device.system_fs}:/"
                                f"{file_info['Filename']} no-prompt"
                            )
                        if device.os == "ASA":
                            device.dis.send_command(
                                f"delete /noconfirm {device.system_fs}:/"
                                f"{file_info['Filename']}"
                            )
                        if device.os == "IOS" or device.os == "IOS-XE":
                            device.dis.send_command(
                                f"delete /force {device.system_fs}:/"
                                f"{file_info['Filename']}"
                            )
                    else:
                        # If single pass, give the specific error.
                        if single_pass:
                            if xfr_exp.args[1] == 0x00:
                                reason = "GENERAL_ERROR"
                            elif xfr_exp.args[1] == 0x3f:
                                reason = "INTERRUPTED_TRANSFER" 
                            elif xfr_exp.args[1] == 0xbf:
                                reason = "PARTIAL_TRANSFER"
                            elif xfr_exp.args[1] == 0xdf:
                                reason = "INTEGRITY_CHECK_FAILED"
                        # Not single pass, and we've exhausted retries.
                        else:
                            reason = "MAX_ATTEMPTS_REACHED"
                # Host unresponsive or file not exist. Do not retry.
                elif xfr_exp.args[1] == 0x7f:
                    xfr_retry = -1
                    nmri.log_message(
                        "warn", f"Repo {repo_addr} unreachable or target"
                        " upgrade file not found. See session log for more"
                        " details."
                    )
                    reason = "NOTCONNECT_OR_FILENOTEXIST"
                # API error
                elif xfr_exp.args[1] == 0xff:
                    xfr_retry = -1
                    nmri.log_message("error", "API error occurred.")
                    reason = "API_ERROR"
            # Unhandled exception
            else:
                xfr_retry = -1
                nmri.log_message("error", f"Unhandled exception: {xfr_exp}")
                reason = "UNHANDLED_EXCEPTION"
    # Complete failure.
    else:
        err = f"Transfer failed ({reason})"
        nmri.log_message("error", err)
        raise Exception(err)
    # Success.
    return


def main(nmri):
    # Instantiate the current device (CiscoDevice class)
    device = CiscoDevice(nmri)

    nmri.log_message("notif",
                     f"Begin {device.os} Software Transfer")

    # Check if this is a non-admin ASA context. Raise exception if it is.
    if (device.os == "ASA"
            and device.asa_multi_context and not device.asa_admin_context):
        parentName = getattr(device.device.parent_device,
                             "DeviceName", "Unknown")
        parentIPDotted = getattr(device.device.parent_device,
                                 "DeviceIPDotted", "")
        # Notify and raise exception.
        nmri.log_message("error", "ASA context detected, but is not admin. "
                        "Check or run job for parent device"
                        f" '{parentName}' ({parentIPDotted})")

        raise Exception("Non-admin ASA context detected. See custom log for"
                        " details.")
    # Is this a VDC?
    if (device.os == "NX-OS"
            and device.nxos_vdc and not device.nxos_default_vdc):
        parentName = getattr(device.device.parent_device,
                             "DeviceName", "Unknown")
        parentIPDotted = getattr(device.device.parent_device,
                                 "DeviceIPDotted", "")
        nmri.log_message("error", "NX-OS VDC detected, but this is not the"
                         " default VDC. Check or run job for parent device"
                        f" '{parentName}' ({parentIPDotted})")
        raise Exception("Non-default VDC for Nexus. See custom log for"
                        " details.")
    # Is this ACI?
    if device.nxos_aci_mode:
        nmri.log_message("error", "NX-OS in ACI mode is not supported."
                         " Please upgrade manually.")
        raise Exception("Nexus ACI mode upgrade not supported.")


    # Let's continue.
    nmri.log_message("info", 
                     f"Interacting with: {device.hostname} ({device.model})")

    # Call CiscoDevice.get_system_image_info() to determine the current
    # running system image, the sys image prefix, and the file system it's
    # stored on.
    device.get_system_image_info()
    nmri.log_message("info", f"Detected platform prefix is: {device.platform}")
    nmri.log_message("info", "Current system image is:"
                     f" {device.current_system_image_fs}:/"
                     f"{device.current_system_image}")

    if device.os == "IOS-XE":
        nmri.log_message("info", 
                         f"This device is in {device.iosxe_boot_mode} mode.")

    # Get fs names and their free space
    device.get_system_fs_info()

    if device.current_system_image_fs != device.system_fs:
        nmri.log_message("warn", "The current running image is not"
                         " stored on the default file system.")

    # TODO: For now, we don't support SD-WAN.
    if device.os == "IOS-XE" and device.iosxe_sdwan['mode']:
        nmri.log_message("error", "IOS-XE SD-WAN is not supported.")
        raise Exception("IOS-XE SD-WAN is not supported.")

    # Get target upgrade image file information
    nmri.log_message("notif", 'Searching for target upgrade image from list'
                     f' "{hash_list}" ...')

    # Get the list ID that contains the software hashes
    os_hash_list_id = get_list_id(nmri, hash_list)

    # Get the target upgrade filename, size, and hash from the list.
    upgrade_file_info = get_upgrade_file_info(nmri, device, os_hash_list_id)
    nmri.log_message("info", "Upgrade image selected:"
                            f" {upgrade_file_info['Filename']}"
                            f", size: {upgrade_file_info['Size']} bytes.")

    # Get kickstart upgrade filename.
    if device.os == "NX-OS" and device.nxos_kickstart_image:
        ks_upgrade_info = get_upgrade_file_info(nmri, device,
                                                os_hash_list_id, True)
        nmri.log_message("info", "Kickstart upgrade image selected:"
                                f" {ks_upgrade_info['Filename']}, size:"
                                f" {ks_upgrade_info['Size']} bytes.")

    # Check if device is already running the target upgrade image.
    already_running_current = False
    if device.iosxe_boot_mode == "INSTALL":
        if f".{device.iosxe_build}." in upgrade_file_info['Filename']:
            already_running_current = True
    if upgrade_file_info['Filename'].startswith(device.current_system_image):
        already_running_current = True

    if already_running_current:
        nmri.log_message("notif", f"{device.hostname} is already running"
                         " the target upgrade image.")
        return # back to __main__

    # Check if the target upgrade image already exists.
    f_exists = device.get_file_size_info(device.system_fs,
                                         upgrade_file_info['Filename'])
    f_exists_and_valid = False

    # If this device is a NX-OS /w kickstart, then check if the target
    # kickstart upgrade already exists.
    ks_exists = (None,-1)
    ks_exists_and_valid = False
    # Only send if it's actually NX-OS /w kickstart.
    if device.os == "NX-OS" and device.nxos_kickstart_image:
        ks_exists = device.get_file_size_info(device.systemfs,
                                              ks_upgrade_info['Filename'])

    # Target upgrade already exists, check if we need to continue or not.
    if f_exists[0]:
        nmri.log_message("notif", "Target upgrade image already exists on this"
                         " device. Verifying integrity ...")
        f_exists_and_valid = verify_image_integrity(upgrade_file_info, device)
        severity = "notif" if f_exists_and_valid else "warn"
        result = "passed" if f_exists_and_valid else "failed"
        nmri.log_message(severity, f"Integrity check {result}.")
        # Target upgrade exists, is valid,
        # and this device isn't a NX-OS /w kickstart.
        if f_exists_and_valid and not ks_exists[0]:
            return

    # Kickstart image exists. Check if we continue or not.
    if ks_exists[0]:
        nmri.log_message("notif", "Kickstart upgrade image already exists on"
                         " this device. Verifying integrity ...")
        ks_exists_and_valid = verify_image_integrity(ks_upgrade_info, device)
        severity = "notif" if ks_exists_and_valid else "warn"
        result = "passed" if ks_exists_and_valid else "failed"
        nmri.log_message(severity, f"Integrity check {result}.")
        # Both the system image and kickstart exist, and both are validated.
        # Nothing to do.
        if f_exists_and_valid and ks_exists_and_valid:
            return

    # File exists, but failed verification.
    if ((f_exists[0] and not f_exists_and_valid)
            or (ks_exists[0] and not ks_exists_and_valid)):
        nmri.log_message("notif", "Continuing with transfer.")

    # If user checked "clean old images", then call remove_old_images() early.
    if clean_old_images:
        nmri.log_message("notif", "Forcefully removing old images ...")

        fs_list = [item['fs'] for item in device.system_fs_info.values()]
        remove_old_images(nmri, device, fs_list)
        # Refresh fs info to get updated free space after old image deletion. 
        device.get_system_fs_info()

    # Check if there is enough free space.
    nmri.log_message("notif", f"Checking if {len(device.system_fs_info)}"
                     " file system(s) has sufficient space for target upgrade"
                     " image ...")
    
    # NX-OS with kickstart. Account size for system + kickstart.
    if device.os == "NX-OS" and device.nxos_kickstart_image:
        req_sz = ks_upgrade_info['Size'] + upgrade_file_info['Size']
    # Everything else.
    else:
        req_sz = upgrade_file_info['Size']

    # Build fs_validated
    fs_validated = validate_fs_space_available(nmri, req_sz,
                                               device.system_fs_info)

    # Notify if pass or fail. Change severity and message accoringly.
    if fs_validated['pass']:
        severity = "notif"
        result = "PASSED"
        num_fs = len(device.system_fs_info)
    else:
        severity = "warn"
        result = "FAILED"
        num_fs = len(fs_validated['fs'])
    nmri.log_message(
        severity, f"Free space validation {result} for {num_fs} file system(s)"
    )

    if not fs_validated['pass']:
        # Handle differently if the user requested
        # to attempt storage reclamation
        if reclaim and not clean_old_images:
            nmri.log_message("info", "Attempting to reclaim storage space ...")
            # Send the failed fs list for old image deletion.
            fs_list = fs_validated['fs']
            remove_old_images(nmri, device, fs_list)
            # Get updated free space from file systems
            nmri.log_message("info",
                             f"Re-checking {len(device.system_fs_info)} file"
                             " system(s) for free space ...")
            device.get_system_fs_info()
            # Call validate_fs_space_available()
            # again, and check if we freed enough space.
            fs_validated = validate_fs_space_available(nmri, req_sz, 
                                                       device.system_fs_info)

        # Not enough free space to store target image.
        # Manual intervention is required.
        # (fs has bad sectors? other large file(s)/dir(s) exist?)
        if not fs_validated['pass']:
            nmri.log_message("error", f"Insufficient space available for"
                             " target upgrade image.")
            if dry_run:
                nmri.log_message("debug", "Insufficient free space")
            else:
                raise Exception("Insufficient free space")

    # Get the remote destination information
    if ovr_repo:
        repo_addr = repo_host_override
        nmri.log_message("notif", f"Repo host override. Using: {repo_addr}")
    else:
        nmri.log_message("notif", "Selecting repo for network view "
                        f'"{device.device.virtual_network.VirtualNetworkName}"'
                        f", region: {repo_region} ...")
        #TODO: Make the list a UI variable
        repo_list_id = get_list_id(nmri, "Cisco OS SW Regional Repos")
        repo_addr = get_repo_info(
            repo_list_id,
            repo_region,
            device.device.virtual_network.VirtualNetworkName
        )

    # Begin transfer
    if not f_exists_and_valid:
        nmri.log_message("notif", "Starting transfer of upgrade image ...")
        xfer_handler(nmri, repo_addr, upgrade_file_info, device, max_retries)
    # Do NX-OS kickstart, if need be.
    #TODO: Change this to "supplemental image"
    if (device.os == "NX-OS"
            and device.nxos_kickstart_image and not ks_exists_and_valid):
        nmri.log_message("notif",
                         "Starting transfer of kickstart upgrade image ...")
        xfer_handler(nmri, repo_addr, ks_upgrade_info, device, max_retries)

    # Copy to other file systems, if required.
    if ((device.os == "IOS" or device.os == "IOS-XE")
            and len(device.system_fs_info) > 1):
        for item in list(device.system_fs_info.values())[1:]:
            # Start at the 2nd key. We don't need key 0 (default fs), because
            # that's what we just transferred to.
            nmri.log_message("notif", "Copying"
                                f" {upgrade_file_info['Filename']}"
                                f" to '{item['fs']}' ...")
            cmd = (f"copy {device.system_fs}:/{upgrade_file_info['Filename']}"
                   f" {item['fs']}:/{upgrade_file_info['Filename']}\r\r\r")
            if dry_run:
                nmri.log_message("debug", f"dry-run cmd: {cmd}")
            else:
                # Use send_async_command, otherwise long copy operations
                # will time out. 1 hour timeout should suffice.
                device.dis.send_async_command(cmd, 3600, "")

    # TODO: Do we need to copy any where other than bootflash?
    #if device.os == "NX-OS":


    # Success
    return

if __name__ == "__main__":
    # Store global variables from the UI.
    clean_old_images = True if clean_old_images == "on" else False
    dry_run = True if dry_run == "on" else False
    reclaim = True if attempt_storage_space_reclaim_if_full == "on" else False
    ovr_repo = True if override_automatic_repo_selection == "on" else False
    # TODO: Check repo_host_override .. is it an IP? Is it valid?
    if ovr_repo and repo_host_override == "IP Address":
        raise Exception("Invalid repo override host.")
    # xfer retries
    try:
        max_retries = int(max_retries)
        if max_retries < 0:
            raise ValueError
    except ValueError:
        raise Exception("Max retries must be a positive integer.")
    except TypeError:
        raise Exception("Max retries must be an integer.")

    # Make sure slash appears at beginning of repo_directory_path.
    if repo_directory_path != "Directory path":
        while repo_directory_path.startswith("/"):
            repo_directory_path = repo_directory_path.lstrip("/")

        repo_directory_path = "/" + repo_directory_path.lstrip("/")

        while repo_directory_path.endswith("/"):
            repo_directory_path = repo_directory_path.rstrip("/")
    # Change the default value from UI to blank
    else:
        repo_directory_path = ""

    enable_debug = True if enable_debug == "on" else False

    easyparams = {
        "api_url": api_url,
        "http_username": http_username,
        "http_password": http_password,
        "job_id": job_id,
        "device_id": device_id,
        "batch_id": batch_id,
    }

    with NetMRIEasy(enable_debug, **easyparams) as nmri:
        main(nmri)
    nmri.log_message("notif", "Software transfer completed.")
