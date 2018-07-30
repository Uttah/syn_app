<template>
  <span>
    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="title">Удаление</span>
        </v-card-title>
        <v-card-text>
          <span >Удалить схему {{this.selectedSchemaNameData}}?</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDialog" :loading="loading">Отмена</v-btn>
          <v-btn flat @click="deleteSchema" :loading="loading">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-select
      v-model="selectedSchemaNameData"
      label="Новая схема"
      :items="filterSchemasData"
      item-text="name"
      item-value="name"
      single-line
      max-height="auto"
    >
      <template slot="selection" slot-scope="data">
        <div class="ellipsis" style="width: 85%">
          {{ data.item.name }}
        </div>
        <v-spacer/>
        <v-btn class="pa-0 ma-0" title="Удалить схему фильтров" flat icon @click.stop="confirmDelete(data.item.id)">
          <v-icon>delete</v-icon>
        </v-btn>
      </template>
      <template slot="item" slot-scope="data">
        <v-list-tile-content v-text="data.item.name" @click="schemaSelect(data.item.filtersSchema)"/>
      </template>
    </v-select>
  </span>
</template>

<script>
  import {deleteFiltersRow} from './query'

  export default {
    name: 'SelectFiltersRow',
    props: {
      filterSchemas: Array,
      selectedSchemaName: String,
      myFilter: Array
    },
    data () {
      return {
        dialog: false,
        loading: false,
        myFilterData: [],
        selectedSchemaNameData: '',
        filterSchemasData: [],
        idDeletedSchema: null
      }
    },
    methods: {
      schemaSelect (val) {
        this.myFilterData = JSON.parse(val)
        this.$emit('update:myFilter', this.myFilterData)
      },
      confirmDelete (val) {
        this.idDeletedSchema = val
        this.dialog = true
      },
      deleteSchema () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: deleteFiltersRow,
            variables: {
              input: {
                id: this.idDeletedSchema
              }
            }
          }
        ).then(({data}) => {
          this.selectedSchemaNameData = ''
          this.filterSchemasData = this.filterSchemasData.filter(currentValue => {
            if (currentValue.id !== this.idDeletedSchema) {
              return currentValue
            }
          })
          this.closeDialog()
          this.loading = false
        }).catch(({data}) => {
          this.loading = false
        })
      },
      closeDialog () {
        this.dialog = false
      }
    },
    watch: {
      selectedSchemaNameData: {
        handler: function (val) {
          this.$emit('update:selectedSchemaName', val)
        },
        deep: true
      },
      filterSchemas: {
        handler: function (val) {
          this.filterSchemasData = val
        },
        deep: true
      }
    }
  }
</script>
