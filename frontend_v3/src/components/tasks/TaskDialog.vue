<template>
  <v-dialog v-model="dialog" persistent lazy max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Изменение задачи</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid">
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <projects-select currentGip label="Проект" v-model="innerInput.projectId" disabled/>
              </v-flex>
              <v-flex xs12>
                <v-text-field
                  label="Новое название задачи"
                  v-model="innerInput.name"
                  :rules="nonEmptyField"
                  required
                />
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="loading" @click.native="openDeleteDialog" :loading="loading">Удалить</v-btn>
        <v-btn flat :disabled="!valid || loading" @click.native="renameTask" :loading="loading" :rules="nonEmptyField">Изменить
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="deleteDialog" max-width="300px">
      <v-card>
        <v-card-title>
          <span class="title">Удаление</span>
        </v-card-title>
        <v-card-text>
          <span>Удалить задачу?</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn @click="closeDeleteDialog">Отмена</v-btn>
          <v-btn @click="removeTask">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>


<script>
  import ProjectsSelect from '../ProjectsSelect'
  import {editTask, removeTask} from './query'

  export default {
    name: 'TaskDialog',
    props: {
      input: {
        id: Number,
        projectId: Number,
        name: String
      }
    },
    components: {
      ProjectsSelect
    },
    data () {
      return {
        dialog: false,
        deleteDialog: false,
        valid: false,
        loading: false,
        innerInput: {
          id: null,
          projectId: null,
          name: ''
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      openDialog () {
        this.dialog = true
        this.innerInput = this.input
      },
      closeDialog () {
        this.dialog = false
      },
      closeDeleteDialog () {
        this.deleteDialog = false
      },
      renameTask () {
        this.loading = true
        this.$apollo.mutate({
          mutation: editTask,
          variables: {
            input: {
              name: this.innerInput.name,
              idTask: this.innerInput.id
            }
          }
        }).then(() => {
          this.loading = false
          this.closeDialog()
        }).catch(() => {
          this.loading = false
        })
      },
      openDeleteDialog () {
        this.deleteDialog = true
      },
      removeTask () {
        this.loading = true
        this.$apollo.mutate({
          mutation: removeTask,
          variables: {
            input: {
              idTask: this.innerInput.id
            }
          }
        }).then(({data}) => {
          if (data.deleteTask.result) {
            this.$emit('tasksChanged')
            this.closeDeleteDialog()
            this.closeDialog()
            this.loading = false
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
