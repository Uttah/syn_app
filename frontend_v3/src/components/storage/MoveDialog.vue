<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <v-card>
      <v-card-title>
        <span class="title">Перемещение</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid">
          <span>
            Перемещение "{{item.goodKind.code}} - {{item.goodKind.name}} ({{item.goodKind.manufacturer.name}})"
            со склада "{{item.location.name}}"
          </span>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs4 class="pr-2">
                <float-field label="Количество" :rules="isNumber" v-model="count" required
                             :suffix="item.unit.shortName"/>
              </v-flex>
              <v-flex xs4 class="px-2">
                <projects-select label="Проект" clearable v-model="projectId"/>
              </v-flex>
              <v-flex xs4 class="pl-2">
                <workers-select label="Ответственный" required v-model="responsibleId"/>
              </v-flex>
              <v-flex xs1 class="pt-4">
                <span>на</span>
              </v-flex>
              <v-flex xs11>
                <storage-select v-model="newWarehouse" required check-state/>
              </v-flex>
              <v-spacer/>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="closeDialog" :loading="loading">Отменить</v-btn>
        <v-btn flat @click="changeWarehouse" :disabled="!valid" :loading="loading">Переместить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import StorageSelect from '../StorageSelect'
  import FloatField from '../FloatField'
  import {changeWarehouse} from './query'
  import ProjectsSelect from '../ProjectsSelect'
  import WorkersSelect from '../WorkersSelect'

  export default {
    name: 'MoveDialog',
    components: {
      WorkersSelect,
      ProjectsSelect,
      StorageSelect,
      FloatField
    },
    data () {
      return {
        item: {
          goodKind: {
            name: null,
            code: null,
            manufacturer: {
              name: null
            }
          },
          location: {
            name: null
          },
          unit: {
            shortName: null
          }
        },
        dialog: false,
        valid: false,
        loading: false,
        newWarehouse: null,
        count: null,
        projectId: null,
        responsibleId: null,
        isNumber: [
          text => {
            if (Number(text) > this.item.count) {
              return this.item.count + ' ' + this.item.unit.shortName + ' в наличии'
            }
            if (Number(text) <= 0) {
              return 'Количество должно быть больше нуля'
            }
            return true
          }
        ]
      }
    },
    methods: {
      openDialog (goodKind, subRow) {
        this.dialog = true
        this.item.goodKind = goodKind
        this.item.location = subRow.location
        this.item.unit = subRow.unit
        this.item.count = subRow.count
        this.item.goodKind = goodKind
        this.item.id = subRow.id
        this.count = this.item.count
      },
      closeDialog () {
        this.dialog = false
      },
      changeWarehouse () {
        this.loading = true
        this.$apollo.mutate({
          mutation: changeWarehouse,
          variables: {
            input: {
              oldWarehouse: this.item.location.id,
              newWarehouse: this.newWarehouse,
              idGood: this.item.id,
              count: this.count,
              projectId: this.projectId,
              responsibleId: this.responsibleId
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.dialog = false
          this.$emit('success')
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
