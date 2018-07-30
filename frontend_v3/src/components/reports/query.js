import gql from 'graphql-tag'

const tableQuery = gql`
query($paged: PagedInput!, $filters: ReportsFilter, $gip: Boolean) {
  reportTableItems: pagedReports(paged: $paged, filters: $filters, gip: $gip) {
    reports {
      id
      worker {
        id
        shortName
      }
      funcRole {
        id
        name
      }
      reportDate
      task
      timeSpent
      timeFrom
      timeTo
      comment
      place {
        id
        name
        kind
      }
      process {
        id
        name
      }
      subProcess {
        id
        name
        kind
      }
      projects {
        id
        number
        description
        gip {
          id
          shortName
        }
      }
      whereFrom
      whereTo
      distance
      gas
      car
      vcProject
      vcDigits
      vcDigitsMinor
      model
      qualityGrade
      timeGrade
      checkedBy {
        id
      }
      deleted
      recordCounted
      moneySpent
      nightShift
    }
    totalCount
  }
}`

const allFuncRoles = gql`
query {
  allFuncRolesData: allFuncRoles {
    id
    name
  }
}`

const allStates = gql`
query {
  allStatesData: allStates {
    id
    name
    deleted
  }
}`

const allProcesses = gql`
query {
  allProcessesData: allProcesses {
    id
    name
    deleted
  }
}`

const allSubProcesses = gql`
query {
  allSubProcessesData: allSubProcesses {
    id
    process
    name
    deleted
  }
}`

const allProjects = gql`
query($search: String, $gip: IntID, $require: [IntID], $currentGip: Boolean){
  allProjectsData: allProjects(search: $search, gip: $gip, require: $require, currentGip: $currentGip) {
    id
    number
    description
    gip {
      id
    }
    state {
      id
      letter
    }
    comment
  }
}`

const allForFill = gql`
query{
  allFuncRoles{
    id
    name
    kind
  }
  allStates {
    id
    name
  }
  allProcesses {
    id
    name
    kind
    subprocessSet {
     id
     name
     kind
    }
  }
  allPlaces {
    id
    name
    kind
   }
}`

const updateConfirmReport = gql`
mutation ($report: UpdateReportInput!, $report2: ConfirmReportInput!, $doConfirm: Boolean!, $skipUpdate: Boolean!) {
  confirmReport(input: $report2) @include(if: $doConfirm) {
    report {
      id
      checkedBy {
        id
        shortName
      }
      timeChecked
    }
  }
  updateReport(input: $report) @skip(if: $skipUpdate) {
    report {
      id
      checkedBy {
        id
        shortName
      }
      timeChecked
      qualityGrade
      timeGrade
      comment
    }
  }
}`
export {tableQuery, allFuncRoles, allStates, allProcesses, allSubProcesses, allProjects, allForFill, updateConfirmReport}
