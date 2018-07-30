import gql from 'graphql-tag'

const hoursProjectsStats = gql`
query ($date: String!) {
  hours(date: $date) {
    reports {
      reportDate
      sum
      projects
      dayOff
    }
    monthSum
  }
  projectsStats(date: $date) {
    project
    sum
  }
  workingDays (date: $date) {
    date
  }
}`
export {hoursProjectsStats}
