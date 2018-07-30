import gql from 'graphql-tag'

const tableQuery = gql`
query ($input: PagedInput!) {
  userTableItems: pagedUsers(paged: $input) {
    totalCount
    users {
      id
      fullName
      positions
      birthDate
      email
      workPhone
      personalPhone
      fired
    }
  }
}`

const addUserQuery = gql`
mutation ($input: AddUserInput!) {
  addUser(input: $input) {
    user {
      id
    }
  }
}`

export {tableQuery, addUserQuery}
