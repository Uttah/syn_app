import gql from 'graphql-tag'

const getNotice = gql`
query {
  getNotice {
    id
    created {
      shortName
    }
    date
    text
    type
    link
  }
}`

const getAllNotice = gql`
query {
  getAllNotice {
    date
    created {
      shortName
    }
    text
  }
}
`
const confirmNotification = gql`
mutation ($input: ConfirmNotificationInput!) {
  confirmNotification (input: $input) {
    result
  }
}
`

export {getNotice, getAllNotice, confirmNotification}
