import gql from 'graphql-tag'

const allBonuses = gql`
query {
  allBonuses {
    id
    userAdded {
      id
      shortName
    }
    timeAdded
    user {
      id
      shortName
    }
    project {
      id
      number
      description
      state {
        id
        letter
      }
    }
    amount
    cash
    installments
    description
    month
    counted
  }
}`

const createBonus = gql`
mutation($input: CreateBonusInput!) {
  createBonus(input: $input) {
    bonus {
      id
    }
  }
}
`

const deleteBonus = gql`
mutation($input: DeleteBonusInput!) {
  deleteBonus(input: $input) {
    result
  }
}
`

const updateBonus = gql`
mutation($input: UpdateBonusInput!) {
  updateBonus(input: $input) {
    bonus {
      id
    }
  }
}
`

export {allBonuses, createBonus, deleteBonus, updateBonus}
