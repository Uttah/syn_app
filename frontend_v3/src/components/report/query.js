import gql from 'graphql-tag'

const createReport = gql`
mutation($report: CreateReportInput!) {
  createReport(input: $report) {
    report {
      id
      worker {
        id
      }
      reportDate 
      funcRole{
        id
      }
      process {
        id
      }
      subProcess {
        id
      }
      task 
      timeSpent 
      place {
        id
      }
      distance 
      car 
      gas 
      whereFrom 
      whereTo 
      moneySpent
      vcProject
      vcDigits
      vcDigitsMinor
      model
      nightShift
    }
  }
}`

const deleteReport = gql`
mutation($report: DeleteReportInput!) {
  deleteReport(input: $report) {
    result
  }
}`

const confirmReport = gql`
mutation($report: ConfirmReportInput!) {
  confirmReport(input: $report) {
    report {
      id
    }
  }
}`

const restoreReport = gql`
mutation($report: RestoreReportInput!) {
  restoreReport(input: $report) {
    result
  }
}`

const updateReport = gql`
mutation($report: UpdateReportInput!) {
  updateReport(input: $report) {
    report {
      id
      timeEdited
      userAdded {
        id
        shortName
      }
      worker {
        id
        shortName
        funcRoles
      }
      reportDate 
      funcRole{
        id
      }
      projects {
        id
        number
        description
        state {
          id
          letter
        }
        gip {
          id
        }
      }
      process {
        id
      }
      subProcess {
        id
      }
      tasks {
        id
      }
      task 
      timeSpent
      timeFrom
      timeTo
      place {
        id
        name
        kind
      }
      distance 
      car 
      gas 
      whereFrom 
      whereTo 
      moneySpent
      vcProject
      vcDigits
      vcDigitsMinor
      model
      qualityGrade
      timeGrade
      comment
      checkedBy {
        id
        shortName
      }
      timeChecked
      nightShift
      recordCounted
      deleted
    }
  }
}`

const getReport = gql`
query($reportId: IntID!) {
  getReportData: getReport(reportId: $reportId) {
    id
    timeEdited
    userAdded {
      id
      shortName
    }
    worker {
      id
      shortName
      funcRoles
    }
    reportDate 
    funcRole{
      id
    }
    projects {
      id
      number
      description
      state {
        id
        letter
      }
      gip {
        id
      }
    }
    process {
      id
    }
    subProcess {
      id
    }
    tasks {
      id
    }
    task 
    timeSpent
    timeFrom
    timeTo
    place {
      id
      name
      kind
    }
    distance 
    car 
    gas 
    whereFrom 
    whereTo 
    moneySpent
    vcProject
    vcDigits
    vcDigitsMinor
    model
    qualityGrade
    timeGrade
    comment
    checkedBy {
      id
      shortName
    }
    timeChecked
    nightShift
    recordCounted
    deleted
  }
}
`
export {createReport, deleteReport, updateReport, confirmReport, restoreReport, getReport}
