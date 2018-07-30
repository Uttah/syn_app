import gql from 'graphql-tag'

const registryCollisionsStateProjects = gql`
query {
  registryCollisionsStateProjects {
    project {
      number
      description
    }
    reports {
      id
    }
    sumHours
  }
}
`

export {registryCollisionsStateProjects}
