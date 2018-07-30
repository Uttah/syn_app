<template>
  <v-dialog v-model="dialog" persistent max-width="750px">
    <v-btn color="submit" slot="activator">Добавить сотрудника</v-btn>
    <v-form v-model="valid">
      <v-card>
        <v-card-title class="headline">Новый сотрудник</v-card-title>
        <v-card-text>
          <v-container class="py-0">
            <v-layout row wrap justify-center>
              <v-flex xs4 class="pr-2">
                <v-text-field label="Фамилия" required v-model="newUser.lastName" :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs4 class="px-2">
                <v-text-field label="Имя" required v-model="newUser.firstName" :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs4 class="pl-2">
                <v-text-field label="Отчество" v-model="newUser.patronym"/>
              </v-flex>
              <v-flex xs4 class="pr-2">
                <v-text-field label="Логин" required v-model="newUser.login" :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs4 class="px-2">
                <v-text-field label="Пароль" required v-model="newUser.password" :rules="passwordField"
                              type="password"/>
              </v-flex>
              <v-flex xs4 class="pl-2">
                <v-text-field label="Подтверждение" required v-model="confirmation" :rules="passwordField"
                              type="password"/>
              </v-flex>
              <v-flex xs6 class="px-2">
                <date-picker v-model="newUser.hireDate" label="Дата приёма" required :rules="nonEmptyField" />
              </v-flex>
              <v-flex xs6 class="px-2">
                <v-select
                  label="Компания"
                  :items="allCompaniesData"
                  item-text="name"
                  item-value="id"
                  v-model="newUser.company"
                  clearable
                  hide-details
                  required
                  :rules="nonEmptyField"
                ></v-select>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <span class="subheading ml-3 error--text" v-if="!passwordsMatch">Пароли не совпадают</span>
          <v-spacer/>
          <v-btn color="blue darken-1" flat @click.native="dialog = false" :disabled="loading">Закрыть</v-btn>
          <v-btn color="blue darken-1" flat @click.native="addUser" :disabled="!valid || loading" :loading="loading">
            Добавить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
  import {addUserQuery} from './query'
  import DatePicker from '../DatePicker.vue'
  import {allCompanies} from '../financial_info/query'

  export default {
    name: 'UserCreateDialog',
    components: {
      DatePicker
    },
    apollo: {
      allCompaniesQuery: {
        fetchPolicy: 'cache-and-network',
        query: allCompanies,
        update (data) {
          data.companies.forEach(company => {
            this.allCompaniesData.push({
              id: company.client.id,
              name: company.client.name
            })
          })
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        dialog: false,
        loading: false,
        allCompaniesData: [],
        newUser: {
          lastName: '',
          firstName: '',
          patronym: '',
          login: '',
          password: '',
          hireDate: null,
          company: null
        },
        confirmation: '',
        valid: false,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        passwordField: [
          text => !!text || 'Пароль не может быть пустым',
          text => text.length >= 8 || 'Минимум 8 символов'
        ]
      }
    },
    methods: {
      addUser () {
        if (this.valid) {
          this.loading = true
          this.$apollo.mutate({
            mutation: addUserQuery,
            variables: {
              input: this.newUser
            }
          }).then(({data}) => {
            this.loading = false
            if (data.addUser.user) {
              this.dialog = false
              this.$emit('userAdded', data.addUser.user.id)
            }
          })
        }
      }
    },
    computed: {
      passwordsMatch () {
        return this.newUser.password === this.confirmation
      }
    }
  }
</script>
