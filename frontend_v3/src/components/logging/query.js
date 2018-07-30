import gql from 'graphql-tag'

const allJournal = gql`
query ($modelName: String!, $instanceId: Int) {
  loggingData: allJournal (modelName: $modelName, instanceId: $instanceId) {
    date
    user {
      id
      shortName
    }
    instance
    change
  }
}`

export {allJournal}
