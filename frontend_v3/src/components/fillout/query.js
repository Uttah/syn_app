import gql from 'graphql-tag'

const tableQuery = gql`
query($paged: PagedInput!, $date: String!) {
  filloutTableItems: pagedFillouts(paged: $paged, date: $date) {
    fillouts {
      hasWorkDays
      daysMissing
      shortName
    }
    totalCount
  }
}`

export {tableQuery}
