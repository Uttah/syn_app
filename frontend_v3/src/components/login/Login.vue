<template>
  <v-container grid-list-md>
    <v-layout row justify-center>
      <v-flex xs4 class="pt-5">
        <login-dialog/>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import LoginDialog from './LoginDialog.vue'

  export default {
    components: {LoginDialog},
    name: 'Login'
  }
</script>
