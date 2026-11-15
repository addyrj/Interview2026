// Linux App Service plan + Node 20 web app. Not deployed here (no Azure CLI).
param location string = resourceGroup().location
param appName string = 'myapp-${uniqueString(resourceGroup().id)}'

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: { reserved: true } // required for Linux
}

resource app 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  kind: 'app,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      alwaysOn: true
      healthCheckPath: '/health'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'NODE_ENV', value: 'production' }
        { name: 'WEBSITE_RUN_FROM_PACKAGE', value: '1' }
      ]
    }
  }
}

// Staging slot for zero-downtime swap (Standard tier or above required).
// Uncomment after changing sku to S1:
// resource staging 'Microsoft.Web/sites/slots@2023-01-01' = {
//   parent: app
//   name: 'staging'
//   location: location
//   properties: { serverFarmId: plan.id }
// }

output url string = 'https://${app.properties.defaultHostName}'
