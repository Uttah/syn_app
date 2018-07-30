import gql from 'graphql-tag'

const changeState = gql`
mutation($input: ProjectStateChangeInput!) {
  projectStateChange(input: $input) {
   result
  }
}`

export {changeState}
