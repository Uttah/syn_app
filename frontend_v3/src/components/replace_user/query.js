import gql from 'graphql-tag'

const replaceUser = gql`
mutation ($input: ReplaceUserInput!) {
    replaceUser(input: $input) {
      result
    }
}`
export {replaceUser}
