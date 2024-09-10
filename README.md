# Azure Function for Service Principal Secret Rotation

This Azure Function is designed to automatically rotate the secrets of a Service Principal when they are near expiry. The function is triggered by an event from Azure Event Grid, which is initiated by Azure Key Vault.