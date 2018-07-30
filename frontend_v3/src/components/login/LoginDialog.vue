<template>
  <v-card color="grey lighten-4" raised class="py-4 px-5">
    <v-form ref="form" v-model="valid" @submit.prevent="submit">
      <img :src="logo" width="100%" class="mb-3 pa-2">
      <v-text-field label="Логин" :rules="loginRules" v-model="login" @blur="clearLogin" required/>
      <v-text-field label="Пароль" :rules="passRules" v-model="password" required
                    :append-icon="passwordVisible ? 'visibility' : 'visibility_off'"
                    :append-icon-cb="() => (passwordVisible = !passwordVisible)"
                    :type="passwordVisible ? 'password' : 'text'"
      />
      <div style="display: flex; justify-content: center">
        <v-btn type="submit" :disabled="loading" color="submit" :loading="loading">Войти</v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script>
  import logo from '../../assets/logo2.0.png'
  import auth from '../../auth/auth'

  export default {
    name: 'login-dialog',
    metaInfo: {
      title: 'Вход для сотрудников ООО "Синергия"'
    },
    methods: {
      clearLogin () {
        let val = this.login
        if (/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,6})+$/.test(val)) {
          val = val.toLowerCase()
        }
        val = val.replace(/\s+/g, '')
        this.login = val
      },
      submit () {
        this.loading = true
        auth.login(this.login, this.password).then(success => {
          this.requestFail = !success
          if (success) {
            this.$apollo.provider.defaultClient.resetStore().then(() => {
              let redirect = this.$route.query.redirect
              if (!redirect) {
                redirect = {name: 'default'}
              }
              this.$emit('loginSuccess')
              if (this.$route.name === 'login') {
                this.$router.replace(redirect)
              }
            })
          } else {
            this.$refs.form.validate()
            this.requestFail = false
          }
          this.loading = false
        })
      }
    },
    data () {
      return {
        logo: logo,
        login: '',
        password: '',
        valid: false,
        requestFail: false,
        passwordVisible: true,
        loading: false,
        loginRules: [
          (v) => !!v || 'Необходимо ввести логин',
          () => this.requestFail ? 'Проверьте логин' : true
        ],
        passRules: [
          (v) => !!v || 'Необходимо ввести пароль',
          () => this.requestFail ? 'Проверьте пароль' : true
        ]
      }
    }
  }
</script>
