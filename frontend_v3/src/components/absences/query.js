import gql from 'graphql-tag'

const tableQuery = gql`
query ($input: PagedInput!, $filters: AbsenceFilter!) {
  absencesTable: pagedAbsences(paged: $input, filters: $filters) {
    totalCount
    absences {
      id
      userAdded {
        shortName
      }
      timeAdded
      worker {
        id
        shortName
      }
      begin
      end
      time
      reason {
        id
        name
      }
      comment
      locked
    }
  }
}`

const addAbsence = gql`
mutation ($input: AddAbsenceInput!) {
  addAbsence(input: $input) {
    absence {
      id
    }
  }
}
`

const updateAbsence = gql`
mutation ($input: UpdateAbsenceInput!) {
  updateAbsence(input: $input) {
    absence {
      id
      userAdded {
        shortName
      }
      timeAdded
      worker {
        id
        shortName
      }
      begin
      end
      time
      reason {
        id
        name
      }
      comment
      locked
    }
  }
}
`

const deleteAbsence = gql`
mutation ($input: DeleteAbsenceInput!) {
  deleteAbsence(input: $input) {
    success
  }
}`

const absenceWorkingDays = gql`
query ($begin: Date!, $end: Date, $workingDays: Int) {
  absenceWorkingDays (begin: $begin, end: $end, workingDays: $workingDays) {
    end
    workingDays
  }
}`

export {tableQuery, addAbsence, updateAbsence, deleteAbsence, absenceWorkingDays}
