# Azure Function for Rotating Service Principal Secrets  
  
This Azure Function is designed to rotate secrets for a Service Principal when a near-expiry-secret event is triggered by Azure Key Vault and placed in an Azure Event Grid topic.  
  
## Prerequisites  
  
1. **Azure Subscription:** Ensure you have an active Azure subscription.  
2. **Azure Key Vault:** Set up an Azure Key Vault to store and manage secrets.  
3. **Event Grid:** Configure an Azure Event Grid topic to trigger the function.  
4. **Managed Identity:** Assign a user-assigned managed identity to the Azure Function for authentication.  
5. **Microsoft Graph API Permissions:** Ensure the managed identity has appropriate permissions to interact with the Microsoft Graph API.  
  
## Setup  
  
1. **Clone the repository:**  
  
    ```sh  
    git clone <repository-url>  
    cd <repository-directory>  
    ```  
  
2. **Update Configuration:**  
  
    Open the Python script and replace the placeholders with your actual Azure subscription details.  
  
    ```python  
    # Replace with your Azure subscription ID  
    subscription_id = "Enter Subscription ID here"  
  
    # Replace with your Entra tenant ID  
    tenant_id = 'Enter Tenant ID here'  
  
    # Client ID of the user-assigned managed identity  
    client_id = "Enter Client ID of managed identity here" 

    # days before expiry to rotate the secret
    validity_period_days = 365 
  
    # Key Vault URI where the secret is stored  
    key_vault_uri = "https://rotation-kv01.vault.azure.net/"  
    ```  
  
3. **Deploy the Function:**  
  
    Deploy the function to Azure using the Azure CLI or the Azure portal.  
  
    ```sh  
    az functionapp deployment source config-zip -g <resource-group> -n <function-app-name> --src <path-to-zip>  
    ```  
  
## Functionality  
  
The function performs the following tasks:  
  
1. **Authentication:**  
  
   Authenticates using the managed identity and retrieves an access token for the Microsoft Graph API.  
  
2. **Trigger:**  
  
   The function is triggered by an event from Azure Event Grid when a Key Vault secret is near expiry.  
  
3. **Retrieve Service Principal Information:**  
  
   Retrieves the Service Principal name from the event data and fetches the object ID of the Service Principal using the Microsoft Graph API.  
  
4. **Generate New Secret:**  
  
   Generates a new secret with an expiry date defined by `validity_period_days` from the current date.  
  
5. **Add New Secret:**  
  
   Adds the new secret to the Service Principal using the Microsoft Graph API.  
  
6. **Store New Secret:**  
  
   Stores the new secret value in Azure Key Vault.  
  
## Logging  
  
The function logs various stages of its execution, including:  
- Properties of the event grid event  
- Event data  
- Service Principal object ID  
- Success or failure of the secret rotation  
- Storage of the new secret in Key Vault  
  
## Usage  
  
Once deployed, the function will automatically trigger and rotate secrets when a near-expiry-secret event is detected. Ensure that the Event Grid is correctly configured to send the relevant events to the function.  
  
## Troubleshooting  
  
- **Authentication Errors:** Ensure that the managed identity is correctly assigned and has the necessary permissions.  
- **Event Trigger:** Verify that the Event Grid is properly configured to trigger the function.  
- **API Permissions:** Ensure the managed identity has the required permissions to interact with the Microsoft Graph API.  
  
## License  
  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  
