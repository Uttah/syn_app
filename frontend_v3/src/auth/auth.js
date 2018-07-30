import Vue from 'vue'
import gql from 'graphql-tag'

const auth = new Vue({
  data: {
    client: null,
    user: {
      id: 0,
      shortName: '',
      isSuperuser: false,
      permissions: []
    }
  },
  methods: {
    async loggedIn () {
      try {
        let {data} = await this.client.query({
          query: gql`{
            currentUser {
              id
              shortName
              isSuperuser
            },
            currentUserPermissions
          }`
        })
        if (data.currentUser) {
          this.user.id = data.currentUser.id
          this.user.isSuperuser = data.currentUser.isSuperuser
          this.user.shortName = data.currentUser.shortName
          this.user.permissions = data.currentUserPermissions
        }
        return data.currentUser !== null
      } catch (e) {
        return false
      }
    },
    async login (name, password) {
      try {
        let {data} = await this.client.mutate({
          mutation: gql`
            mutation ($params: LoginInput!) {
              login(input: $params) {
                success,
                user {
                  id
                  shortName
                  isSuperuser
                }
              }
          }`,
          variables: {
            params: {
              login: name,
              password: password
            }
          }
        })
        if (data.login.success) {
          this.user.id = data.login.user.id
          this.user.isSuperuser = data.login.user.isSuperuser
          this.user.shortName = data.login.user.shortName
          const {data: perms} = await this.client.query({
            fetchPolicy: 'network-only',
            query: gql`{
              currentUserPermissions
            }`
          })
          this.user.permissions = perms.currentUserPermissions
        } else {
          this.user.id = 0
          this.user.shortName = ''
          this.user.isSuperuser = false
          this.user.permissions = []
        }
        return data.login.success
      } catch (e) {
        return false
      }
    },
    async getPermissions () {
      let loggedIn = await this.loggedIn()
      if (loggedIn) {
        try {
          let {data} = await this.client.query({
            fetchPolicy: 'network-only',
            query: gql`{
              currentUserPermissions
            }`
          })
          this.user.permissions = data.currentUserPermissions
          return data.currentUserPermissions
        } catch (e) {
          return []
        }
      } else {
        return []
      }
    },
    hasPermission (permName) {
      if (this.user.isSuperuser) {
        return true
      } else {
        return this.user.permissions.indexOf(permName) > -1
      }
    },
    async logout () {
      if (this.loggedIn()) {
        try {
          let {data} = await this.client.mutate({
            mutation: gql`
              mutation {
                logout {
                  success
                }
              }`
          })
          if (data.logout.success) {
            this.user.id = 0
            this.user.shortName = ''
            this.user.isSuperuser = false
            this.user.permissions = []
          }
          return data.logout.success
        } catch (e) {
          return false
        }
      } else {
        return false
      }
    }
  }
})

export default auth
