import gql from 'graphql-tag'

const allSalaryInMonth = gql`
query ($userId: IntID, $date: String!, $companyFilter: IntID) {
  allSalaryInMonth (userId: $userId, date: $date, companyFilter: $companyFilter) {
    users {
      user {
        shortName
        fired
      }
      months {
        month
        totals {
          workHours
          overtime
          home
          welding
          healthyDay
          transportOffice
          night
          positiveGrade
          negativeGrade
          idealGrade
          order
          workHoursMoney
          overtimeMoney
          homeMoney
          weldingMoney
          healthyDayMoney
          nightMoney
          positiveGradeMoney
          negativeGradeMoney
          idealGradeMoney
          transportMoney
          privateCar
          dutyCar
          transportOfficeMoney
          orderMoney
          vacationMoney
        }
      }
      totals {
        workHours
        overtime
        home
        welding
        healthyDay
        transportOffice
        night
        positiveGrade
        negativeGrade
        idealGrade
        order
        workHoursMoney
        overtimeMoney
        homeMoney
        weldingMoney
        healthyDayMoney
        nightMoney
        positiveGradeMoney
        negativeGradeMoney
        idealGradeMoney
        transportMoney
        privateCar
        dutyCar
        transportOfficeMoney
        orderMoney
        vacationMoney
      }
      bonus
      advance
    }
    totals {
      workHours
      overtime
      home
      welding
      healthyDay
      transportOffice
      night
      positiveGrade
      negativeGrade
      idealGrade
      order
      workHoursMoney
      overtimeMoney
      homeMoney
      weldingMoney
      healthyDayMoney
      nightMoney
      positiveGradeMoney
      negativeGradeMoney
      idealGradeMoney
      transportMoney
      privateCar
      dutyCar
      transportOfficeMoney
      orderMoney
      vacationMoney
    }
  }
}`

const userSalaryInfo = gql`
query ($date: String!) {
  userSalaryInfo (date: $date) {
    salary
    base
    costHour
    advance
    general
    welding
    experience
    etech
    schematic
    initiative
    discipline
    myGeneral
    myWelding
    myExperience
    myEtech
    mySchematic
    myInitiative
    myDiscipline
    avg
    baseCostHour
    workHoursInMonth
  } 
}`

const userSalaryBonusInfo = gql`
query ($date: String) {
  userSalaryBonusInfo (date: $date) {
    description
    amount
    cash
    installments
  }
}`

const allGradeCoefficients = gql`
query {
  allGradeCoefficients {
    quality
    time
    coefficient
  }
}`

const accruals = gql`
query {
  accruals {
    id
    name
    accruals {
      user
      auto
      other
      bonus
      advance
      mainPart
    }
  }
}`

const closeSalary = gql`
mutation {
  closeSalary {
    result
  }
}`

const lastSalaryMonth = gql`
query {
  lastSalaryMonth
}`

export {
  allSalaryInMonth,
  userSalaryInfo,
  closeSalary,
  allGradeCoefficients,
  userSalaryBonusInfo,
  accruals,
  lastSalaryMonth
}
