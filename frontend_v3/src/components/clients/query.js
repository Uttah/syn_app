import gql from 'graphql-tag'

const tableQuery = gql`
query($paged: PagedInput!, $filters: ClientFilter) {
  clientsTableItems: pagedClients(paged: $paged, filters: $filters) {
    clients {
      id
      name
      fullName
      INN
      KPP
      OKPO
      OGRN
      legalAddress
      streetAddress
      phoneNumber
      manager {
        id
        shortName
      }
      other
      kind {
        id
        name
      }
      relation {
        id
        name
      }
    }
    totalCount
  }
}`

const deleteClient = gql`
mutation ($input: DeleteClientInput!) {
  deleteClient(input: $input ) {
    result
  }
}`

const editClient = gql`
mutation ($input: EditClientInput!) {
  editClient(input: $input ) {
    result
  }
}`

const createClient = gql`
mutation ($input: AddClientInput!) {
  addClient(input: $input ) {
    client {
      id
      name
    }
  }
}`

const pagedContacts = gql`
query($paged: PagedInput!, $filters: ContactFilter) {
  pagedContacts: pagedContacts(paged: $paged, filters: $filters) {
    contacts {
      id
      lastName
      firstName
      patronum
      position
      phoneNumber
      client {
        id
        name
        manager {
          id
        }
      }
    }
    totalCount
  }
}`

const createContact = gql`
mutation ($input: AddContactInput!) {
  addContact(input: $input ) {
    result
  }
}`

const editContact = gql`
mutation ($input: EditContactInput!) {
  editContact(input: $input ) {
    result
  }
}`

const deleteContact = gql`
mutation ($input: DeleteContactInput!) {
  deleteContact(input: $input ) {
    result
  }
}`

const pagedClientHistories = gql`
query ($paged: PagedInput!, $filters: ClientHistoryFilter) {
  pagedClientHistories (paged: $paged, filters: $filters) {
    clientHistory {
      id
      client {
        id
        name
        manager {
          id
        }
      }
      contacts {
        id
        lastName
        firstName
        patronum
        phoneNumber
        position
      }
      date
      interaction
      result
      nextStepDate
      nextStep
      wasDeleted
    },
    totalCount
  }
}
`

const createClientHistory = gql`
mutation ($input: AddClientHistoryInput!) {
  addClientHistory(input: $input) {
    result
  }
}`

const deleteClientHistory = gql`
mutation ($input: DeleteClientHistoryInput!) {
  deleteClientHistory(input: $input) {
    result
  }
}`

const editClientHistory = gql`
mutation ($input: EditClientHistoryInput!) {
  editClientHistory(input: $input) {
    result
  }
}`

const allClients = gql`
query {
  allOwnClients {
    id
    name
  }
}`

export {tableQuery, deleteClient, editClient, createClient, pagedContacts, createContact, editContact, deleteContact, pagedClientHistories,
  createClientHistory, deleteClientHistory, editClientHistory, allClients}
