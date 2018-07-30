import gql from 'graphql-tag'

const tableQuery = gql`
query ($input: PagedInput!, $filters: OccupationFilter!) {
  pagedOccupations(paged: $input, filters: $filters) {
    totalCount
    occupations {
      id
      user {
        id
        shortName
        positions
        fired
      }
      salary
      base
      advance
      fraction
      byHours
      fixedHour
      transportation
      mainCompany {
        id
        client {
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
    shortName
    client {
      id
      name
    }
    positionSet {
      id
      name
    }
  }
}`

const updateOccupation = gql`
mutation ($input: UpdateOccupationInput!) {
  updateOccupation(input: $input) {
    occupation {
      id
      user {
        id
        shortName
        positions
      }
      salary
      base
      advance
      fraction
      byHours
      fixedHour
      transportation
      mainCompany {
        id
        client {
          id
          name
        }
      }
    }
  }
}`

export {tableQuery, allCompanies, updateOccupation}
