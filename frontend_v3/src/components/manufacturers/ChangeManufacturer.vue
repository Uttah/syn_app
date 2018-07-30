<template>
  <v-dialog v-model="dialog" persistent max-width="750px" width="750px">
    <v-form v-model="valid">
      <v-card>
        <v-card-title>
          <span class="headline" style="width: 100%">Смена производителя у товаров</span>
          <span class="subheading" v-if="deletionProcess" style="width: 100%">
            Удаляемый производитель используется несколькими видами товара, перед удалением необходимо заменить
            его на другого.
          </span>
        </v-card-title>
        <v-card-text>
          <v-layout row wrap justify-center>
            <v-flex xs5 class="mr-2">
              <manufacturer-select v-model="input.oldId" label="Старый производитель" required/>
            </v-flex>
            <v-flex xs5 class="ml-2">
              <manufacturer-select v-model="input.newId" label="Новый производитель" required/>
            </v-flex>
          </v-layout>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="closeDialog" :loading="loading">Закрыть</v-btn>
          <v-btn flat @click.native="changeManufacturer" :disabled="!valid" :loading="loading">Сменить</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
  import {changeManufacturer} from './query'
  import ManufacturerSelect from '../ManufacturerSelect'

  export default {
    name: 'ChangeManufacturer',
    components: {
      ManufacturerSelect
    },
    data () {
      return {
        dialog: false,
        loading: false,
        valid: false,
        input: {
          oldId: null,
          newId: null
        },
        deletionProcess: false
      }
    },
    methods: {
      openDialog (oldId) {
        this.dialog = true
        if (oldId) {
          this.input.oldId = oldId
          this.deletionProcess = true
        }
      },
      closeDialog () {
        this.dialog = false
      },
      changeManufacturer () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: changeManufacturer,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          if (data.changeManufacturer.result) {
            this.$emit('changed')
            this.loading = false
            this.dialog = false
            this.deletionProcess = false
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
