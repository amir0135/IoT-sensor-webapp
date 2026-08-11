@description('Primary location for all resources.')
param location string

@description('Region for the Azure Data Explorer cluster.')
param adxLocation string

@description('Azure Data Explorer SKU name. Dev SKUs use the Basic tier; others use Standard.')
param adxSkuName string = 'Dev(No SLA)_Standard_E2a_v4'

@description('Region for the Static Web App.')
param staticWebAppLocation string

@description('Tags applied to every resource.')
param tags object

@description('Unique-ish token used to build resource names.')
param resourceToken string

@description('Azure Data Explorer database name.')
param databaseName string = 'IoTDatabase'

@description('Azure Data Explorer table name the API queries.')
param tableName string = 'IoTSensorData'

// Dev SKUs run on the Basic tier with a single instance; everything else is Standard (min 2).
var adxIsDev = startsWith(adxSkuName, 'Dev')
var adxTier = adxIsDev ? 'Basic' : 'Standard'
var adxCapacity = adxIsDev ? 1 : 2

// ---------------------------------------------------------------------------
// Frontend — Azure Static Web App
// ---------------------------------------------------------------------------
resource web 'Microsoft.Web/staticSites@2023-12-01' = {
  name: 'web-${resourceToken}'
  location: staticWebAppLocation
  tags: union(tags, { 'azd-service-name': 'web' })
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: 'claryo-frontend'
      outputLocation: 'build'
    }
  }
}

// ---------------------------------------------------------------------------
// Data — Azure Data Explorer (Kusto) cluster, database, schema
// ---------------------------------------------------------------------------
resource adx 'Microsoft.Kusto/clusters@2023-08-15' = {
  name: 'adx${resourceToken}'
  location: adxLocation
  tags: tags
  sku: {
    name: adxSkuName
    tier: adxTier
    capacity: adxCapacity
  }
  properties: {
    enableStreamingIngest: true
  }
}

resource adxDb 'Microsoft.Kusto/clusters/databases@2023-08-15' = {
  parent: adx
  name: databaseName
  location: adxLocation
  kind: 'ReadWrite'
  properties: {}
}

// Create the table the API expects, idempotently.
resource adxSchema 'Microsoft.Kusto/clusters/databases/scripts@2023-08-15' = {
  parent: adxDb
  name: 'create-schema'
  properties: {
    scriptContent: '.create-merge table ${tableName} (timestamp: datetime, sensorId: string, temperature: real, pressure: real, flowRate: real)'
    continueOnErrors: false
  }
}

// ---------------------------------------------------------------------------
// Backend — Linux App Service (Python), system-assigned managed identity
// ---------------------------------------------------------------------------
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

resource api 'Microsoft.Web/sites@2023-12-01' = {
  name: 'api-${resourceToken}'
  location: location
  tags: union(tags, { 'azd-service-name': 'api' })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'python -m uvicorn main:app --host 0.0.0.0 --port 8000'
      ftpsState: 'Disabled'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'KUSTO_CLUSTER'
          value: adx.properties.uri
        }
        {
          name: 'KUSTO_DB'
          value: databaseName
        }
        {
          name: 'KUSTO_TABLE'
          value: tableName
        }
        {
          name: 'AUTH_MODE'
          value: 'default'
        }
        {
          name: 'ALLOWED_ORIGINS'
          value: 'https://${web.properties.defaultHostname}'
        }
      ]
    }
  }
}

// Grant the backend's managed identity read access to the ADX database.
resource adxAccess 'Microsoft.Kusto/clusters/databases/principalAssignments@2023-08-15' = {
  parent: adxDb
  name: 'api-viewer'
  properties: {
    principalId: api.identity.principalId
    principalType: 'App'
    role: 'Viewer'
    tenantId: subscription().tenantId
  }
}

output API_BASE_URL string = 'https://${api.properties.defaultHostName}'
output WEB_URL string = 'https://${web.properties.defaultHostname}'
output KUSTO_CLUSTER string = adx.properties.uri
output KUSTO_DB string = databaseName
output KUSTO_TABLE string = tableName
