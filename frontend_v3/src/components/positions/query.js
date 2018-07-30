import gql from 'graphql-tag'

const positionsQuery = gql`
query ($userId: IntID!) {
  positions: userPositions(userId: $userId) {
    id
    salary
    base
    advance
    fraction
    byHours
    user {
      id
      shortName
    }
  }
}`

const pagedPositionsQuery = gql`
query ($input: PagedInput!, $showFired: Boolean, $filters: OccupationFilter!) {
  positionsPaged: pagedUserPositions(paged: $input, showFired: $showFired, filters: $filters) {
    totalCount
    positions: occupations {
      id
      salary
      base
      advance
      fraction
      byHours
      user {
        id
        shortName
      }
      position {
        id
        name
        company {
          id
          name
        }
      }
    }
  }
}`

const allCompanies = gql`
query {
  companies: allCompanies {
    id
    client {
      id
      name
    }
    shortName
    positions: positionSet {
      id
      name
    }
  }
}`

const allUsers = gql`
query {
  users: allUsers {
    id
    shortName
  }
}`

const allUsersAndPositions = gql`
query {
  allUsersAndPositions {
    userId
    positionId
    user
    position
  }
}`

const addPosition = gql`
mutation ($input: AddOccupationInput!) {
  addOccupation(input: $input) {
    occupation {
      id
      salary
      base
      advance
      fraction
      byHours
      position {
        id
        name
        company {
          id
          name
        }
      }
      user {
        id
        shortName
      }
    }
  }
}`

const deletePositions = gql`
mutation ($input: DeleteOccupationsInput!) {
  deleteOccupations(input: $input) {
    success
  }
}`

const updateOccupation = gql`
mutation ($input: UpdateOccupationInput!) {
  updateOccupation(input: $input) {
    occupation {
      id
      salary
      base
      advance
      fraction
      byHours
      user {
        id
        shortName
      }
      position {
        id
        name
        company {
          id
          name
        }
      }
    }
  }
}`

const assignPosition = gql`
mutation ($input: AssignPositionInput!) {
  assignPosition (input: $input) {
    result
  }
}`

const removePosition = gql`
mutation ($input: RemovePositionInput!) {
  removePosition (input: $input) {
    result
  }
}`

export {
  positionsQuery,
  allCompanies,
  allUsers,
  allUsersAndPositions,
  addPosition,
  deletePositions,
  pagedPositionsQuery,
  updateOccupation,
  assignPosition,
  removePosition
}
