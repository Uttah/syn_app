import gql from 'graphql-tag'

const userQuery = gql`
query ($userId: IntID!) {
  user(userId: $userId) {
    id
    fullName
    shortName
    lastName
    firstName
    patronym
    workPhone
    personalPhone
    email
    login
    gender
    birthDate
    healthy
    hireDate
    fireDate
    isSuperuser
    fired
    head {
      id
      shortName
    }
    avatar
  }
}`

const modifyUser = gql`
mutation ($input: ModifyUserInput!) {
  modifyUser(input: $input) {
    user {
      id
      fullName
      shortName
      lastName
      firstName
      patronym
      workPhone
      personalPhone
      email
      login
      gender
      birthDate
      healthy
      hireDate
      fireDate
      isSuperuser
      fired
      head {
        id
        shortName
      }
      avatar
    }
  }
}`

const changeUserPassword = gql`
mutation ($input: ChangePasswordInput!) {
  changeUserPassword(input: $input) {
    success
  }
}`

const fireUser = gql`
mutation ($input: FireUserInput!) {
  fireUser(input: $input) {
    success
  }
}`

const hireUser = gql`
mutation ($input: HireUserInput!) {
  hireUser(input: $input) {
    success
  }
}`

const setSuperUser = gql`
mutation ($input: SetSuperUserInput!) {
  setSuperUser(input: $input) {
    success
  }
}`

const saveUserAvatar = gql`
mutation ($input: SaveUserAvatarInput!) {
  saveUserAvatar (input: $input) {
    imagePath
  }
}`

export {userQuery, changeUserPassword, modifyUser, fireUser, hireUser, setSuperUser, saveUserAvatar}
