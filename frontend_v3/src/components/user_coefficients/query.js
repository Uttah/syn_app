import gql from 'graphql-tag'

const allCoefficients = gql`
query {
  allCoefficients {
    id
    user {
      shortName
    }
    general
    welding
    experience
    etech
    schematic
    initiative
    discipline
    maxHour
    avg
    base
  }
}`

const updateCoefficients = gql`
mutation ($input: UpdateCoefficientsInput!) {
  updateCoefficients(input: $input) {
    coefficients {
      id
      user {
        shortName
      }
      general
      welding
      experience
      etech
      schematic
      initiative
      discipline
      maxHour
      avg
      base
    }
  }
}`
export {allCoefficients, updateCoefficients}
