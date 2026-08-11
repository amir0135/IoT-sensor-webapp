targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the azd environment — used to derive resource names.')
param environmentName string

@minLength(1)
@description('Primary location for all resources (e.g. westeurope, eastus2).')
param location string

@description('Region for the Static Web App (must be a Static Web Apps region).')
@allowed([
  'westus2'
  'centralus'
  'eastus2'
  'westeurope'
  'eastasia'
])
param staticWebAppLocation string = 'westeurope'

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    staticWebAppLocation: staticWebAppLocation
    tags: tags
    resourceToken: resourceToken
  }
}

output AZURE_LOCATION string = location
output API_BASE_URL string = resources.outputs.API_BASE_URL
output REACT_APP_API_URL string = resources.outputs.API_BASE_URL
output WEB_URL string = resources.outputs.WEB_URL
output KUSTO_CLUSTER string = resources.outputs.KUSTO_CLUSTER
output KUSTO_DB string = resources.outputs.KUSTO_DB
output KUSTO_TABLE string = resources.outputs.KUSTO_TABLE
