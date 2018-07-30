<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title class="title">
        Создание задачи для позиций
      </v-card-title>
      <v-card-text>
        Вы действительно хотите создать задачу для позиций?
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="dialog=false">Отмена</v-btn>
        <v-btn flat :loading="loading" @click="createTaskFunc">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {createTaskForPositions} from './query'

  export default {
    name: 'create-task-for-positions-dialog',
    props: [
      'value',
      'positions'
    ],
    data () {
      return {
        dialog: false,
        loading: false
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
      createTaskFunc () {
        this.loading = true
        this.$apollo.mutate({
          mutation: createTaskForPositions,
          variables: {
            input: {
              positions: this.positions
            }
          }
        }).then(({data}) => {
          if (data.createTaskForPositions.result) {
            this.loading = false
            this.$emit('createTaskForPositionsSuccess')
            this.dialog = false
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>

<style scoped>

</style>
