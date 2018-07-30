<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Создание производителя</span>
      </v-card-title>
      <v-card-text>
        <v-form xs12>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <v-text-field label="Название" v-model="input.name" required/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog">Закрыть</v-btn>
        <v-btn flat @click.native="createVendor">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {createVendor} from './query'

  export default {
    name: 'create-vendor',
    props: [
      'value'
    ],
    data () {
      return {
        dialog: false,
        input: {
          name
        }
      }
    },
    watch: {
      value: function (val) {
        this.dialog = val
      },
      dialog: function (val) {
        this.$emit('input', val)
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      createVendor () {
        this.$apollo.mutate(
          {
            mutation: createVendor,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          if (data.createVendor.result) {
            this.dialog = false
          }
        })
      }
    }
  }
</script>

<style scoped>

</style>
