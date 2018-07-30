<template>
  <div class="pl-5 pr-5">
    <workers-select v-model="user" label="Пользователь" required/>
    <v-btn @click="replaceUser">Заменить</v-btn>
  </div>
</template>

<script>
  import {replaceUser} from './query'
  import WorkersSelect from '../WorkersSelect'

  export default {
    components: {WorkersSelect},
    name: 'replace-user',
    metaInfo: {
      title: 'Замена пользователя'
    },
    data () {
      return {
        user: null
      }
    },
    methods: {
      replaceUser () {
        this.$apollo.mutate(
          {
            mutation: replaceUser,
            variables: {
              input: {
                userId: this.user
              }
            }
          }
        ).then(({data}) => {
          if (data.replaceUser.result === true) {
            window.location.replace('/reports')
          }
          if (data.replaceUser.result === false) {
            window.location.replace('/reports')
          }
        })
      }
    }
  }
</script>

<style scoped>

</style>
