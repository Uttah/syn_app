<template>
  <v-dialog v-model="dialog" persistent max-width="750px">
    <v-btn color="submit" slot="activator">Создать задачу</v-btn>
    <v-form v-model="valid">
      <v-card>
        <v-card-title class="headline">Новая задача</v-card-title>
        <v-card-text>
          <v-container class="py-0">
            <v-layout>
              <v-flex xs6 class="pr-2">
                <v-text-field
                  label="Название задачи"
                  v-model="nameNewTask"
                  required
                  :rules="nonEmptyField"
                />
              </v-flex>
              <v-flex xs6 class="pl-2">
                <projects-select currentGip v-model="projectSelectData" label="Проект" required/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="blue darken-1" flat @click.native="dialog = false" :disabled="loading">Закрыть</v-btn>
          <v-btn color="blue darken-1" flat @click.native="createNewTask" :disabled="!valid || loading"
                 :loading="loading">Создать
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
  import ProjectsSelect from '../ProjectsSelect'
  import {createNewTask} from './query'

  export default {
    name: 'CreateTask',
    components: {
      ProjectsSelect
    },
    data () {
      return {
        loading: false,
        valid: false,
        dialog: false,
        projectSelectData: null,
        nameNewTask: '',
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      createNewTask () {
        this.loading = true
        this.$apollo.mutate({
          mutation: createNewTask,
          variables: {
            input: {
              name: this.nameNewTask,
              project: this.projectSelectData
            }
          }
        }).then(() => {
          this.loading = false
          this.dialog = false
          this.$emit('tasksChanged')
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
