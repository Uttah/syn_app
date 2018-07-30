<template>
  <v-card v-if="auth.hasPermission('projects.change_project_state_batch')">
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Смена этапа проекта</span>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-form v-model="valid">
        <v-layout wrap justify-center>
          <v-spacer/>
          <v-flex xs3 class="mx-2">
            <projects-select label="Проекты" multiple v-model="projects" required/>
          </v-flex>
          <v-flex xs3 class="mx-4">
            <project-state-select label="Этап проекта" v-model="state" required/>
          </v-flex>
          <v-flex xs3 class="mx-2">
            <date-picker label="Начиная с даты" v-model="dateFilter" :rules="nonEmptyField" required/>
          </v-flex>
          <v-spacer/>
        </v-layout>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer/>
      <v-btn @click="changeState" :loading="loading" :disabled="!valid" class="success mr-3">Изменить</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
  import ProjectsSelect from '../ProjectsSelect'
  import ProjectStateSelect from '../ProjectStateSelect'
  import DatePicker from '../DatePicker'
  import {changeState} from './query'
  import auth from '../../auth/auth'

  export default {
    name: 'ProjectStateChange',
    metaInfo: {
      title: 'Смена этапа проекта'
    },
    components: {
      ProjectsSelect,
      ProjectStateSelect,
      DatePicker
    },
    data () {
      return {
        loading: false,
        valid: false,
        projects: [],
        state: null,
        dateFilter: null,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        auth: auth
      }
    },
    methods: {
      changeState () {
        this.loading = true
        this.$apollo.mutate({
          mutation: changeState,
          variables: {
            input: {
              projects: this.projects,
              state: this.state,
              dateFilter: this.dateFilter
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Этап изменен'
          })
        }).catch(() => {
          this.loading = false
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Ошибка'
          })
        })
      }
    }
  }
</script>
