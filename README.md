# client-assets-csv-export
This script provides a solution for exporting a list of assets from a single client. This tool adds value since the functionality of exporting client assets to a CSV is currently missing from the platform UI. It allows users to conveniently retrieve and export asset objects, enhancing the overall manageability of assets within the client.

Once exported, assets can be backed up or reimported to a different client. Please see our public docs on how to [import client assets from a CSV](https://docs.plextrac.com/plextrac-documentation/product-documentation/clients/adding-assets-to-a-client#importing-assets-to-clients).

### Important Consideration for CSV Re-Import: Duplicate Assets
We're currently aware that assets with the same name are handled sub-optimally. When importing a CSV of assets, the import process will deduplicate assets based solely on the asset name. If a CSV contains 2 rows where assets share a name, only the data from the last row will be considered. In the Plextrac platform, we deduplicate assets based on a combination of the parent asset's name, if present, and the asset name. Therefore, the existence of rows with the same asset name, need to be highly considered when importing a CSV of assets created from this script. Since a client in Plextrac CAN have multiple assets with the same name if they have different parent assets, this could be a common case to run into and our import process currently isn't able to handle this in a more graceful way.

The only exception is port data. If there are 2 rows that share an asset name, the port data from the first row will combine with any port data on the asset in a later row.

Internal ticket to track this issue: IO-886

# Requirements
- [Python 3+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [pipenv](https://pipenv.pypa.io/en/latest/install/)

# Installing
After installing Python, pip, and pipenv, run the following commands to setup the Python virtual environment.
```bash
git clone this_repo
cd path/to/cloned/repo
pipenv install
```

# Setup
After setting up the Python environment the script will run in, you will need to setup a few things to configure the script before running.

## Credentials
In the `config.yaml` file you should add the full URL to your instance of Plextrac.

The config also can store your username and password. Plextrac authentication lasts for 15 mins before requiring you to re-authenticate. The script is set up to do this automatically through the authentication handler. If these 3 values are set in the config, and MFA is not enabled for the user, the script will take those values and authenticate automatically, both initially and every 15 mins. If any value is not saved in the config, you will be prompted when the script is run and during re-authentication.

# Usage
After setting everything up you can run the script with the following command. You should run the command from the folder where you cloned the repo.
```bash
pipenv run python main.py
```
You can also add values to the `config.yaml` file to simplify providing the script with custom parameters needed to run.

## Required Information
The following values can either be added to the `config.yaml` file or entered when prompted for when the script is run.
- PlexTrac Top Level Domain e.g. https://yourapp.plextrac.com
- Username
- Password

## Script Execution Flow
- Authenticates user to provided instance of Plextrac
- Pulls client data from your instance
- Prompts user to select a client to export assets to a CSV
- Pulls all asset info from the selected client
- Parses asset data and saves in CSV 
