<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-btn color="submit" slot="activator">Добавить производителя</v-btn>
    <v-form v-model="valid">
      <v-card>
        <v-card-title>
          <span class="title">Создание производителя</span>
        </v-card-title>
        <v-card-text>
          <v-layout wrap justify-center>
            <v-flex xs12>
              <v-text-field label="Название" v-model="input.name" :rules="nonEmptyField" required/>
            </v-flex>
          </v-layout>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="closeDialog" :loading="loading">Закрыть</v-btn>
          <v-btn flat @click.native="createManufacturer" :disabled="!valid" :loading="loading">Создать</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
  import {createManufacturer} from './query'

  export default {
    name: 'CreateManufacturer',
    data () {
      return {
        valid: false,
        dialog: false,
        loading: false,
        input: {
          name: ''
        },
        nonEmptyField:
          [
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
      closeDialog () {
        this.dialog = false
      },
      createManufacturer () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createManufacturer,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          if (data.createManufacturer.manufacturer) {
            this.loading = false
            this.dialog = false
            this.$emit('success')
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
