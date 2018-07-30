<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="500px">
    <v-btn color="primary" slot="activator">Назначить ответственного</v-btn>
    <v-card>
      <v-card-title>
        <span class="title">Назначение ответственного</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <projects-select label="Проект" v-model="input.projectId" required clearable/>
              </v-flex>
              <v-flex xs12>
                <workers-select label="Ответственный" v-model="input.responsibleId" required/>
              </v-flex>
              <v-flex xs12>
                <date-picker label="Дата приказа" v-model="input.date" :rules="nonEmptyField" required/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="!valid || loading" @click.native="createOrder" :loading="loading">Назначить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import {createOrder} from './query'
  import ProjectsSelect from '../ProjectsSelect'
  import WorkersSelect from '../WorkersSelect'
  import DatePicker from '../DatePicker'

  export default {
    name: 'CreateOrderDialog',
    components: {
      DatePicker,
      WorkersSelect,
      ProjectsSelect
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        input: {
          projectId: null,
          responsibleId: null,
          date: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      createOrder () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createOrder,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.createOrder.order.id) {
            this.dialog = false
            this.$emit('created')
          }
        })
      }
    }
  }
</script>
