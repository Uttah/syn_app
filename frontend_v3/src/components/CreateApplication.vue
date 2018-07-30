<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="700px">
    <v-card>
      <v-card-title>
        <span class="subheading">Создание Заявки на закупку</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid">
          <v-layout wrap justify-center>
            <v-flex xs5>
              <date-picker v-model="deadline" label="Крайний срок" required :rules="nonEmptyField"/>
            </v-flex>
            <v-flex xs7 class="pl-3">
              <workers-select v-model="worker" label="Ответственные" multiple/>
            </v-flex>
            <v-flex xs10>
              <v-text-field
                label="Название склада закупки"
                :rules="nonEmptyField"
                v-model="locationName"
                required
              />
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="closeDialog" :loading="loading">Отменить</v-btn>
        <v-btn flat @click="create" :loading="loading" :disabled="!valid">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {createApplication} from './storage/query'
  import DatePicker from './DatePicker'
  import WorkersSelect from './WorkersSelect'
  import utilsMixin from './utils'

  export default {
    name: 'CreateApplication',
    components: {
      DatePicker,
      WorkersSelect
    },
    mixins: [
      utilsMixin
    ],
    data () {
      return {
        valid: false,
        dialog: false,
        loading: false,
        specification: null,
        deadline: null,
        locationName: null,
        worker: [],
        nonEmptyField: [
          (text) => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      openDialog (val) {
        this.specification = val
        this.locationName = `Склад ${this.formatProject(val.project.number)} - ${val.pressmark}`
        this.dialog = true
      },
      closeDialog () {
        this.dialog = false
      },
      create () {
        this.loading = true
        this.$apollo.mutate({
          mutation: createApplication,
          variables: {
            input: {
              idSpec: this.specification.id,
              deadline: this.deadline,
              worker: this.worker,
              locationName: this.locationName
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$router.push({
            name: 'logistic_request',
            params: {id: data.createApplication.result}
          })
          this.closeDialog()
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>

