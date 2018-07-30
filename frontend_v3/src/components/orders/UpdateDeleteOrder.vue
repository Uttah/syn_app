<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Обновление ответственного</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <projects-select label="Проект" v-model="input.project" :disabled="disabled" required clearable/>
              </v-flex>
              <v-flex xs12>
                <workers-select label="Ответственный" v-model="input.responsible" :disabled="disabled" required/>
              </v-flex>
              <v-flex xs12>
                <date-picker label="Дата приказа" v-model="input.date" :rules="nonEmptyField" :disabled="disabled" required/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="disabled || loading" @click.native="deleteOrder" :loading="loading">Удалить</v-btn>
        <v-btn flat :disabled="!valid || disabled || loading" @click.native="updateOrder" :loading="loading">Обновить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import {updateOrder, deleteOrder} from './query'
  import ProjectsSelect from '../ProjectsSelect'
  import WorkersSelect from '../WorkersSelect'
  import DatePicker from '../DatePicker'

  export default {
    name: 'UpdateDeleteOrderDialog',
    props: [
      'input'
    ],
    components: {
      DatePicker,
      WorkersSelect,
      ProjectsSelect
    },
    data () {
      return {
        dialog: false,
        valid: false,
        disabled: false,
        loading: false,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    watch: {
      input: function () {
        this.dialog = true
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      deleteOrder () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: deleteOrder,
            variables: {
              input: {id: this.input.id}
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.deleteOrder.result === true) {
            this.dialog = false
            this.$emit('deleted')
          }
        })
      },
      updateOrder () {
        this.loading = true
        let input = {}
        input.id = this.input.id
        input.projectId = (this.input.project && this.input.project.id) ? this.input.project.id : this.input.project
        input.responsibleId = (this.input.responsible && this.input.responsible.id) ? this.input.responsible.id : this.input.responsible
        input.date = this.input.date
        this.$apollo.mutate(
          {
            mutation: updateOrder,
            variables: {
              input: input
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.updateOrder.order.id) {
            this.dialog = false
            this.$emit('updated')
          }
        })
      }
    }
  }
</script>
