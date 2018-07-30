import gql from 'graphql-tag'

const pagedSalaryPayments = gql`
query ($paged: PagedInput) {
  pagedSalaryPayments (paged: $paged) {
    salaryPayments {
      id
      user {
        id
        shortName
      }
      amount
      advance
      company {
        id
        client {
          id
          name
        }
      }
    }
    totalCount
  }
}`

const createSalaryPayment = gql`
mutation ($input: CreateSalaryPaymentInput!) {
  createSalaryPayment (input: $input) {
    result
  }
}`

const updateSalaryPayment = gql`
mutation ($input: UpdateSalaryPaymentInput!) {
  updateSalaryPayment (input: $input) {
    result
  }
}`

const deleteSalaryPayment = gql`
mutation ($input: DeleteSalaryPaymentInput!) {
  deleteSalaryPayment (input: $input) {
    result
  }
}`

export {pagedSalaryPayments, createSalaryPayment, updateSalaryPayment, deleteSalaryPayment}
