<template>
  <div>
    <v-select
      :label="label"
      :required="required"
      :multiple="multiple"
      :disabled="disabled"
      :clearable="clearable"
      :readonly="readonly"
      :hide-details="hideDetails"
      autocomplete
      :rules="rules"
      v-model="storage"
      :items="allStorageData"
      item-text="name"
      item-value="id"
      :search-input.sync="searchStorage"
    >
      <template slot="no-data">
        <span class="subheading">
          <span class="px-2">Местоположение не найдено.</span>
          <v-btn @click="dialog = true">Создать новое</v-btn>
        </span>
      </template>
    </v-select>

    <v-dialog v-model="dialog" persistent max-width="500px">
      <v-card>
        <v-card-title>
            <span class="subheading">
              Создание нового местоположения
            </span>
        </v-card-title>
        <v-card-text>
          <v-text-field label="Местоположение" v-model="newLocationName"/>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="blue darken-1" flat @click.native="dialog = false">Отменить</v-btn>
          <v-btn color="blue darken-1" flat @click.native="saveDialog">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import gql from 'graphql-tag'
  import sorted from 'is-sorted'

  export default {
    name: 'StorageSelect',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Местонахождение'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      checkState: Boolean,
      project: Number
    },
    data () {
      return {
        newLocationName: '',
        dialog: false,
        searchStorage: null,
        storage: [],
        allStorageData: [],
        rules: [
          array => {
            if (this.required) {
              if (array && Array.isArray(array)) {
                return array.length > 0 || 'Поле не может быть пустым'
              } else {
                return !!array || 'Поле не может быть пустым'
              }
            } else {
              return true
            }
          },
          array => {
            if (this.checkState) {
              if (array && Array.isArray(array)) {
                array.forEach(index => {
                  const item = this.allStorageData.find(item => item.id === index)
                  if (!item) {
                    return true
                  }
                  if (item.project.state.id !== '2' && item.project.state.id !== '3' && item.project.state.id !== '4') {
                    return 'Этап проекта не допускает хранение на складе'
                  }
                })
                return true
              } else {
                const item = this.allStorageData.find(item => item.id === array)
                if (!item) {
                  return true
                }
                if (item.project.state.id !== '2' && item.project.state.id !== '3' && item.project.state.id !== '4') {
                  return 'Этап проекта не допускает хранение на складе'
                }
                return true
              }
            } else {
              return true
            }
          }
        ]
      }
    },
    mounted: function () {
      this.assignStorage(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query($search: String, $require: [IntID], $project: IntID){
            allWarehouses(search: $search, require: $require, project: $project){
              id
              name
              project {
                id
                number
                state {
                  id
                }
              }
            }
          }`,
        fetchPolicy: 'network-only',
        update (data) {
          data.allWarehouses.forEach(item => {
            if (this.allStorageData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allStorageData.push(item)
            }
          })
          if (!sorted(this.allStorageData, (a, b) => Number(a.id) - Number(b.id))) {
            this.allStorageData.sort((a, b) => Number(a.id) - Number(b.id))
          }
        },
        variables () {
          return {
            search: this.searchStorage,
            require: this.requiredWarehouse,
            project: Number(this.project)
          }
        }
      }
    },
    methods: {
      saveDialog () {
        this.dialog = false
        this.$emit('newLocationName', this.newLocationName)
      },
      assignStorage (val) {
        if (val) {
          this.storage = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.storage = this.storage.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.storage = this.storage.id
            }
          }
        }
      }
    },
    computed: {
      requiredWarehouse: function () {
        let warehouses = []
        if (this.storage) {
          warehouses = Array.isArray(this.storage) ? this.storage : [this.storage]
        }
        const notLoaded = warehouses.filter(warehouse => {
          return this.allStorageData.findIndex(item => Number(item.id) === Number(warehouse)) < 0
        })
        if (notLoaded.length > 0) {
          return notLoaded
        }
        return null
      }
    },
    watch: {
      value: function (val) {
        this.assignStorage(val)
      },
      storage: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
