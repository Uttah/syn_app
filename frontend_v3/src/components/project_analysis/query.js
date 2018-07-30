import gql from 'graphql-tag'

const projectAnalysisQuery = gql`
query($filters: [AnalysisFilter], $limits: DateRangeType!) {
  dataTreeData: projectAnalysis(filters: $filters, limits: $limits) {
    ...nodeFields
    children {
      ...nodeFields
      children {
        ...nodeFields
        children {
          ...nodeFields
          children {
            ...nodeFields
            children {
              ...nodeFields
              children {
                ...nodeFields
                children {
                  ...nodeFields
                  children {
                    ...nodeFields
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

fragment nodeFields on AnalysisNode {
  name
  hours
  money
}`

const filterSchemas = gql`
query {
  filterSchemas {
    id
    name
    filtersSchema
    userCreated {
      id
    }
  }
}
`

const createFiltersRow = gql`
mutation ($input: CreateFiltersSchemaInput!) {
  createFiltersSchema(input: $input) {
    schema {
      id
      name
      filtersSchema
      userCreated {
        id
      }
    }
  }
}`

const deleteFiltersRow = gql`
mutation ($input: DeleteFiltersSchemaInput!) {
  deleteFiltersSchema(input: $input) {
    result
  }
}`

const getHourPrimeCost = gql`
query {
  getHourPrimeCost
}`

const changeHourPrimeCost = gql`
mutation ($input: ChangeHourPrimeCostInput!) {
  changeHourPrimeCost (input: $input) {
    result
  }
}`

export {projectAnalysisQuery, createFiltersRow, filterSchemas, deleteFiltersRow, getHourPrimeCost, changeHourPrimeCost}
