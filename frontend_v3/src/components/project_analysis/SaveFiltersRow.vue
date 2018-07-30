<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Сохранение схемы фильтров</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid">
          <v-layout wrap justify-center style="align-items: center">
            <v-flex xs4>
              <v-subheader>Введите название</v-subheader>
            </v-flex>
            <v-spacer/>
            <v-flex xs7>
              <v-text-field class="pr-3" label="Название" :rules="nonEmptyField" v-model="nameData" required>
              </v-text-field>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="closeDialog" :loading="loading">Закрыть</v-btn>
        <v-btn flat @click="saveSchema" :loading="loading" :disabled="!valid">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {createFiltersRow} from './query'

  export default {
    name: 'SaveFiltersRow',
    props: {
      filtersRow: String,
      name: String
    },
    data () {
      return {
        dialog: false,
        loading: false,
        valid: false,
        nameData: this.name,
        nonEmptyField: [
          array => {
            if (array && Array.isArray(array)) {
              return array.length > 0 || 'Поле не может быть пустым'
            } else {
              return !!array || 'Поле не может быть пустым'
            }
          }
        ]
      }
    },
    methods: {
      openDialog () {
        this.dialog = true
      },
      closeDialog () {
        this.dialog = false
      },
      saveSchema () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createFiltersRow,
            variables: {
              input: {
                name: this.nameData,
                filtersRow: this.filtersRow
              }
            }
          }
        ).then(({data}) => {
          this.loading = false
          this.closeDialog()
          this.$emit('saved')
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      name: {
        handler: function (val) {
          this.nameData = val
        }
      }
    }
  }
</script>
