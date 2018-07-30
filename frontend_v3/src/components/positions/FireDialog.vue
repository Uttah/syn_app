<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-btn color="fired" :disabled="selectedRows.length < 1" slot="activator">
      {{ selectedRows.length > 1 ? 'Снять с должностей' : 'Снять с должности' }}
    </v-btn>
    <v-card>
      <v-card-title>
        <span class="subheading">
          Вы действительно хотите снять {{ allUsers && selectedRows.length > 1 ? 'сотрудников' : 'сотрудника' }} с
          {{ selectedRows.length > 1 ? 'выбранных должностей' : 'выбранной должности' }}?
        </span>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs10 offset-xs1>
              <date-picker v-model="date" label="Дата увольнения"/>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <span class="subheading ml-3 error--text" v-if="!date">Необходимо указать дату</span>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false" :disabled="loading">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!date || loading" @click.native="fire" :loading="loading">Уволить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import DatePicker from '../DatePicker.vue'
  import {deletePositions} from './query'

  export default {
    name: 'PositionsFireDialog',
    components: {
      DatePicker
    },
    props: ['selectedRows', 'allUsers'],
    data () {
      return {
        dialog: false,
        loading: false,
        date: null
      }
    },
    methods: {
      fire () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deletePositions,
          variables: {
            input: {
              occupationIds: this.selectedRows.map(item => item.id),
              fireDate: this.date
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.deleteOccupations.success) {
            this.dialog = false
            this.$emit('fire')
          }
        })
      }
    }
  }
</script>
