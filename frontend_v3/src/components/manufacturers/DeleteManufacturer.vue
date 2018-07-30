<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Изменение производителя</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid">
          <v-layout wrap justify-space-between>
            <v-flex xs12>
              <v-text-field label="Производитель" :rules="nonEmptyField" v-model="input.name" required/>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat :loading="loading" @click="closeDialog">Закрыть</v-btn>
        <v-btn flat :loading="loading" @click="deleteManufacturer">Удалить</v-btn>
        <v-btn flat :loading="loading" :disabled="!valid" @click="renameManufacturer">Изменить</v-btn>
      </v-card-actions>
    </v-card>
    <change-manufacturer @changed="deleteManufacturer" ref="changeDialog"/>
  </v-dialog>
</template>

<script>
  import {checkManufacturer, deleteManufacturer, renameManufacturer} from './query'
  import ChangeManufacturer from './ChangeManufacturer'

  export default {
    name: 'DeleteManufacturer',
    components: {
      ChangeManufacturer
    },
    props: {
      input: {
        id: Number,
        name: String
      }
    },
    data () {
      return {
        dialog: false,
        loading: false,
        valid: false,
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
      openDialog () {
        this.dialog = true
      },
      closeDialog () {
        this.dialog = false
      },
      deleteManufacturer () {
        this.loading = true
        // Проверка ТУТ
        this.$apollo.query({
          query: checkManufacturer,
          variables: {
            filters: {
              manufacturer: this.input.id
            }
          },
          fetchPolicy: 'network-only'
        }).then(({data}) => {
          if (data.checkManufacturer) {
            // Мутация удаления ТУТ
            this.$apollo.mutate({
              mutation: deleteManufacturer,
              variables: {
                input: {
                  id: this.input.id
                }
              }
            }).then(data => {
              this.loading = false
              this.dialog = false
              this.$emit('success')
            }).catch(() => {
              this.loading = false
            })
          } else {
            // Открыть диалог смены производителя
            this.loading = false
            this.$refs.changeDialog.openDialog(this.input.id)
          }
        }).catch(() => {
          this.loading = false
        })
      },
      renameManufacturer () {
        this.loading = true
        this.$apollo.mutate({
          mutation: renameManufacturer,
          variables: {
            input: {
              id: this.input.id,
              name: this.input.name
            }
          }
        }).then(data => {
          this.loading = false
          this.dialog = false
          // Обновление таблицы
          this.$emit('success')
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
