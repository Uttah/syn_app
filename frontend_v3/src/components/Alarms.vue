<template>
  <div>
    <v-snackbar v-for="(item, index) in errors" :timeout="5000" multi-line
                top v-model="item.show" :key="index" color="error">
      {{ item.message }}
      <v-btn flat icon @click.native="item.show = false">
        <v-icon color="white">close</v-icon>
      </v-btn>
    </v-snackbar>
    <v-dialog v-model="loginDialog && $route.name !== 'login'" persistent max-width="30%">
      <login-dialog @loginSuccess="loginDialog = false"/>
    </v-dialog>
  </div>
</template>

<script>
  import LoginDialog from './login/LoginDialog.vue'

  export default {
    components: {LoginDialog},
    name: 'Errors',
    data () {
      return {
        loginDialog: false,
        errors: []
      }
    },
    methods: {
      push (text) {
        if (text === '') {
          return
        }
        if (text.indexOf('matching query does not exist') > 0) {
          this.$router.replace({name: 'page404'})
          return
        }
        if (text.indexOf('::') > -1) {
          const split = text.split('::', 2)
          text = split[1] || ''
          const code = parseInt(split[0])
          if (code === 401 && this.$router.currentRoute.name && this.$router.currentRoute.name !== 'login') {
            // Необходим логин
            this.loginDialog = true
            return
          }
          if (this.$router.currentRoute.path === '/') {
            return
          }
        }
        const length = this.errors.length
        const last = length > 0 ? this.errors[length - 1] : null
        if (last && last.message === text && last.show) {
          return
        }
        let newError = {
          message: text,
          show: false
        }
        this.errors.push(newError)
        if (this.errors.length > 5) {
          this.errors.shift()
        }
        setTimeout(() => {
          this.errors[this.errors.length - 1].show = true
        }, 50)
      }
    }
  }
</script>
