import yaml
import time
import csv
from copy import deepcopy

import settings
import utils.log_handler as logger
log = logger.log
from utils.auth_handler import Auth
import utils.input_utils as input
import api
import utils.general_utils as utils


def get_page_of_clients(page: int = 0, clients: list = [], total_clients: int = -1) -> None:
    """
    Handles traversing pagination results to create a list of all items.

    :param page: page to start on, for all results use 0, defaults to 0
    :type page: int, optional
    :param clients: the list passed in will be added to, acts as return, defaults to []
    :type clients: list, optional
    :param total_clients: used for recursion to know when all pages have been gathered, defaults to -1
    :type total_clients: int, optional
    """
    payload = {
        "pagination": {
            "offset": page*100,
            "limit": 100
        }
    }
    # EXAMPLE schema of returned clients
    # {
    #     "client_id": 4155,
    #     "name": "Test Client",
    #     "poc": "poc name",
    #     "tags": [
    #         "test"
    #     ]
    # }
    response = api.clients.list_clients(auth.base_url, auth.get_auth_headers(), payload)
    if response.json['status'] != "success":
        log.critical(f'Could not retrieve clients from instance. Exiting...')
        exit()
    total_clients = int(response.json['meta']['pagination']['total'])
    if len(response.json['data']) > 0:
        clients += deepcopy(response.json['data'])

    if len(clients) < total_clients:
        return get_page_of_clients(page+1, clients, total_clients)
    
    return None

def get_page_of_assets(client_id: int, page: int = 0, assets: list = [], total_assets: int = -1) -> None:
    """
    Handles traversing pagination results to create a list of all items.

    :param page: page to start on, for all results use 0, defaults to 0
    :type page: int, optional
    :param assets: the list passed in will be added to, acts as return, defaults to []
    :type assets: list, optional
    :param total_assets: used for recursion to know when all pages have been gathered, defaults to -1
    :type total_assets: int, optional
    """
    log.info(f'Load page {page} of client assets...')
    payload = {
        "pagination": {
            "offset": page*100,
            "limit": 100
        }
    }
    # region EXAMPLE schema of returned assets
        # {
        #     "asset": "Test Asset All Fields",
        #     "assetCriticality": "High",
        #     "id": "cloxe6ukz00t30hrr3rwrfn82",
        #     "parent": {
        #         "asset": "Parent Asset",
        #         "id": "cloxe594h00t20hrrdqjo6sz5"
        #     },
        #     "findings": {
        #         "info": 0,
        #         "low": 0,
        #         "medium": 0,
        #         "high": 0,
        #         "critical": 0,
        #         "total": 0
        #     },
        #     "system_owner": "System Owner",
        #     "type": "Workstation",
        #     "data_owner": "Data Owner",
        #     "hostname": "Hostname",
        #     "operating_system": [
        #         "windows"
        #     ],
        #     "dns_name": "DNS Name",
        #     "host_fqdn": "Host FQDN",
        #     "host_rdns": "Host RDNS",
        #     "mac_address": "MAC Address",
        #     "physical_location": "Physical Location",
        #     "netbios_name": "NetBIOS Name",
        #     "total_cves": "5",
        #     "pci_status": "pass",
        #     "description": "<p><span style=\"background-color:rgb(255,255,255);color:rgb(37,36,40);\">Asset Description</span></p>",
        #     "knownIps": [
        #         "1.1.1.1"
        #     ],
        #     "tags": [
        #         "test"
        #     ],
        #     "ports": {
        #         "1234": {
        #             "number": "1234",
        #             "service": "service",
        #             "protocol": "protocol",
        #             "version": "version"
        #         }
        #     }
        # }
    # endregion
    response = api.clients.list_client_assets(auth.base_url, auth.get_auth_headers(), client_id, payload)
    if response.json['status'] != "success":
        log.critical(f'Could not retrieve assets from instance. Exiting...')
        exit()
    total_assets = int(response.json['meta']['pagination']['total'])
    if len(response.json['data']) > 0:
        assets += deepcopy(response.json['data'])

    if len(assets) < total_assets:
        return get_page_of_assets(client_id, page+1, assets, total_assets)
    
    return None

def get_client_choice(clients) -> int:
    """
    Prompts the user to select from a list of clients to export related assets to CSV.
    Based on subsequently called functions, this will return a valid option or exit the script.

    :param repos: List of clients returned from the POST List Clients endpoint
    :type repos: list[client objects]
    :return: 0-based index of selected client from the list provided
    :rtype: int
    """
    log.info(f'List of Clients:')
    index = 1
    for client in clients:
        log.info(f'{index} - Name: {client["name"]} | ID: {client["client_id"]} | Tags: {client.get("tags", [])}')
        index += 1
    return input.user_list("Select a client to export assets from", "Invalid choice", len(clients)) - 1



if __name__ == '__main__':
    for i in settings.script_info:
        print(i)

    with open("config.yaml", 'r') as f:
        args = yaml.safe_load(f)

    auth = Auth(args)
    auth.handle_authentication()


    # load all clients from instance
    log.info(f'Loading Clients from instance')
    clients = []
    get_page_of_clients(0, clients=clients)
    log.debug(f'list of loaded clients:\n{clients}')
    log.success(f'Loaded {len(clients)} client(s) from instance')


    # prompt user to select a repo for export
    while True:
        choice = get_client_choice(clients)
        if input.continue_anyways(f'Export asset(s) from \'{clients[choice]["name"]}\' to CSV?'):
            break
    selected_client = clients[choice]


    # set file path for exported CSV
    parser_time_seconds: float = time.time()
    parser_time: str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(parser_time_seconds))
    FILE_PATH = f'{utils.sanitize_file_name(selected_client["name"])}_{parser_time}.csv'


    # get all assets in user selected client
    log.info(f'Getting Assets from selected Client')
    assets = []
    get_page_of_assets(selected_client['client_id'], 0, assets=assets)
    log.debug(f'list of loaded assets:\n{assets}')
    log.success(f'Loaded {len(assets)} assets(s) from client')


    # CREATE CSV
    # define headers
    headers = ["name", "ip addresses", "criticality", "data owner", "physical location", "system owner", "ports", "tags",
                "description", "parent", "type", "host fqdn", "hostname", "host rdns", "dns name", "mac address", "netbios name",
                "total cves", "pci status", "operating system"]

    # pluck asset data from API response and format as list for CSV
    csv_assets = []
    for asset in assets:
        # knownIps
        knownIps = str(asset.get('knownIps', "")).replace("[","").replace("]","").replace("'","")
        # ports
        ports = []
        for port in asset.get('ports', {}).values():
            ports.append(f'{port.get("number", "")}//{port.get("protocol", "")}//{port.get("service", "")}//{port.get("version", "")}/')
        ports = str(ports).replace("[","").replace("]","").replace("'","")
        # tags
        tags = str(asset.get('tags', "")).replace("[","").replace("]","").replace("'","")
        # parent
        parent_asset_name = ""
        parent = asset.get("parent", {})
        if isinstance(parent, dict):
            parent_asset_name = parent.get("asset", "")
        # pci status
        pci_status = asset.get("pci_status", "")
        pci_status = "Pass" if pci_status == "pass" else "Fail" if pci_status == "fail" else ""
        # operating system
        operating_system = str(asset.get('operating_system', "")).replace("[","").replace("]","").replace("'","")        
        
        # all fields
        fields_for_csv = [
            asset.get('asset', ""),
            knownIps,
            asset.get('assetCriticality', ""),
            asset.get('data_owner', ""),
            asset.get('physical_location', ""),
            asset.get('system_owner', ""),
            ports,
            tags,
            asset.get('description', ""),
            parent_asset_name,
            asset.get('type', ""),
            asset.get('host_fqdn', ""),
            asset.get('hostname', ""),
            asset.get('host_rdns', ""),
            asset.get('dns_name', ""),
            asset.get('mac_address', ""),
            asset.get('netbios_name', ""),
            asset.get('total_cves', ""),
            pci_status,
            operating_system
        ]

        # add writeup to list to be written to csv
        csv_assets.append(fields_for_csv)

    # WRITE CSV
    with open(FILE_PATH, 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(csv_assets)
    log.success(f'Saved assets to CSV \'{FILE_PATH}\'')