#!/usr/bin/env python3

import argparse, getpass
from infoblox_netmri.client import InfobloxNetMRI

API_VER = "3.3.0"
SECURITY_USE_SSL = True
SECURITY_SSL_VERIFY = False

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--list", type=str, required=True,
    help="Filename that contains list of DeviceIDs to delete.")
parser.add_argument("-n", "--host", type=str, default="netmri",
    help="The hostname or IP address of NetMRI.")
parser.add_argument("-u", "--user", type=str, default="admin",
    help="Username to connect to NetMRI")
parser.add_argument('--unitid', type=int, 
    help="UnitID of collector to send delete request to "
         "(used in OC environment).")


def main():

    args = parser.parse_args()

    NMRI_HOST = args.host
    NMRI_USER = args.user

    print("Connecting to '{}' as '{}' ...".format(NMRI_HOST, NMRI_USER))
    NMRI_PASSWD = getpass.getpass("Password: ", stream=None)

    c = InfobloxNetMRI(
        host=NMRI_HOST,
        username=NMRI_USER,
        password=NMRI_PASSWD,
        api_version=API_VER,
        use_ssl=SECURITY_USE_SSL,
        ssl_verify=SECURITY_SSL_VERIFY
    )

    # Test connection
    try:
        broker = c.get_broker('BasicServices')
        serverinfo = broker.server_info()
    except:
        print("Failed to connect.")
        exit(1)

    print("Connected to '{}' (NetMRI version: {})".format(
        NMRI_HOST, serverinfo['netmri_version']
    ))

    # Open list of DeviceIDs
    try:
        with open(args.list, 'r') as f:
            fileLines = f.readlines()
    except:
        print("Could not open the list file.")
        exit(1)

    # Create comma seperated list of DeviceIDs.
    # To be used for input 'ids' to broker.delete().
    print("Reading {} ...".format(args.list))
    devIdList = ''
    for line in fileLines:
        devIdList += line.replace('\n',',')
    devIdList = devIdList.rstrip(',')
    
    # Send request
    broker = c.get_broker('Device')
    if args.unitid:
        print("Sending deletion request, with UnitID {} ...".format(
            int(args.unitid)
        ))
        broker.delete(ids=devIdList,UnitID=int(args.unitid))
    else:
        print("Sending deletion request ...")
        broker.delete(ids=devIdList)

    print("Done.")
    exit(0)

if __name__ == "__main__":
        main()
