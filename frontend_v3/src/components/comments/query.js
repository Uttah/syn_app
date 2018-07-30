import gql from 'graphql-tag'

const comments = gql`
query ($name: String!, $objectId: Int!) {
  comments (name: $name, objectId: $objectId) {
    id
    objectId
    date
    user {
      id
      shortName
      avatar
    }
    comment
  }
}`

const createComment = gql`
mutation ($input: CreateCommentsInput!) {
  createComments (input: $input) {
    result
  }
}`

export {comments, createComment}
