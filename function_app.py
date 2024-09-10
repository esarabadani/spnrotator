import logging
import azure.functions as func
import sys
import requests
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from datetime import datetime, timedelta, timezone
from azure.keyvault.secrets import SecretClient
from azure.mgmt.authorization import AuthorizationManagementClient

# Replace with your Azure subscription ID
subscription_id = "Enter Subscription ID here"  

# Replace with your Entra tenant ID
tenant_id = 'Enter Tenant ID here'

# Client ID of the user-assigned managed identity
client_id = "Enter Client ID of managed identity here"

# Authenticate using managed identity and get a token
credential = ManagedIdentityCredential(client_id=client_id)
token = credential.get_token("https://graph.microsoft.com/.default")
access_token = token.token

# Define Azure Function. The Function gets triggered using a near-expiry-secret event initiated by Key Vault and placed in Azure Event Grid topic
app = func.FunctionApp()
@app.event_grid_trigger(arg_name="azeventgrid")
def spn(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event')
    properties = dir(azeventgrid)
    logging.info(f'Properties of azeventgrid: {properties}')
    event_data = azeventgrid.get_json()
    logging.info(f'Event data: {event_data}')
    
    # Retrieve the Service Principal name (Key Vault secret name) stored in Key Vault from the event data
    spn_name = event_data.get('ObjectName')
    logging.info(f'ObjectName: {spn_name}')

    # Retrieve the object ID of the Service Principal using Azure REST API
    url = f"https://graph.microsoft.com/v1.0/applications?$filter=displayName eq '{spn_name}'"
    headers = {
       "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    sp_obj_id = response_data['value'][0]['id']
    logging.info(f'Service Principal Object ID: {sp_obj_id}')

    # Define the new secret payload. Expirty date is set to 365 days from the current date
    start_datetime = datetime.now(timezone.utc)
    end_datetime = start_datetime + timedelta(days=365)

    new_secret_value =  str(start_datetime.year)

    secret_payload = {
        "passwordCredential": {
            "displayName": new_secret_value,
            "startDateTime": start_datetime.isoformat() + 'Z',
            "endDateTime": end_datetime.isoformat() + 'Z'
        }
    }
    
    # Add a new secret using Microsoft Graph API
    url = f"https://graph.microsoft.com/v1.0/myorganization/applications/{sp_obj_id}/addPassword"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=secret_payload)
    new_secret_value = response.json()["secretText"]
    
    if response.status_code == 200:
        print(f"Secret rotated successfully. New secret value: {new_secret_value}")
    else:
        print(f"Failed to rotate secret: {response.status_code} - {response.text}")

    # Store the new secret value in Azure Key Vault
    key_vault_uri = "https://rotation-kv01.vault.azure.net/"
    secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret_client.set_secret(spn_name, new_secret_value)
    print(f"New secret stored in Key Vault: {spn_name}")