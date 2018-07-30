import gql from 'graphql-tag'

const tableQuery = gql`
query ($paged: PagedInput!) {
  pagedManufacturers(paged: $paged){
    manufacturers {
      id
      name
    }
    totalCount
  }
}`

const createManufacturer = gql`
mutation ($input: CreateManufacturerInput!) {
  createManufacturer (input: $input) {
    manufacturer {
      id
    }
  }
}`

const changeManufacturer = gql`
mutation ($input: ChangeManufacturerInput!) {
  changeManufacturer (input: $input) {
    result
  }
}`

const checkManufacturer = gql`
query ($filters: GoodsFilter!) {
  checkManufacturer(filters: $filters)
}`

const deleteManufacturer = gql`
mutation ($input: DeleteManufacturerInput!) {
  deleteManufacturer (input: $input) {
    result
  }
}`

const renameManufacturer = gql`
mutation ($input: RenameManufacturerInput!) {
  renameManufacturer (input: $input) {
    result
  }
}`

export {
  tableQuery,
  createManufacturer,
  changeManufacturer,
  checkManufacturer,
  deleteManufacturer,
  renameManufacturer
}
