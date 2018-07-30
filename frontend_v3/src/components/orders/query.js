import gql from 'graphql-tag'

const allOrders = gql`
query {
  allOrders {
    id
    project {
      id
      number
      description
      state {
        id
        letter
      }
    }
    responsible {
      id
      shortName
    }
    date
  }
}`

const createOrder = gql`
mutation($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order {
      id
    }
  }
}`

const deleteOrder = gql`
mutation($input: DeleteOrderInput!) {
  deleteOrder(input: $input) {
    result
  }
}`

const updateOrder = gql`
mutation($input: UpdateOrderInput!) {
  updateOrder(input: $input) {
    order {
      id
    }
  }
}`
export {allOrders, createOrder, deleteOrder, updateOrder}
