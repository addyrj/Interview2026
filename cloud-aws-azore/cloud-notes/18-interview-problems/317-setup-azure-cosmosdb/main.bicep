// Cosmos DB for NoSQL, serverless, one database and container. Not deployed here.
param location string = resourceGroup().location
param accountName string = 'cosmos-${uniqueString(resourceGroup().id)}'

resource account 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: accountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [ { name: 'EnableServerless' } ]
    disableLocalAuth: false // set true and use Entra ID RBAC in production
  }
}

resource db 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: account
  name: 'shop'
  properties: {
    resource: { id: 'shop' }
  }
}

resource orders 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: db
  name: 'orders'
  properties: {
    resource: {
      id: 'orders'
      partitionKey: {
        paths: [ '/customerId' ]
        kind: 'Hash'
        version: 2
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [ { path: '/*' } ]
        excludedPaths: [ { path: '/"_etag"/?' } ]
      }
    }
  }
}

output endpoint string = account.properties.documentEndpoint
