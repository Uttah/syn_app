<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-btn color="submit" slot="activator">Принять обратно</v-btn>
    <v-card>
      <v-card-title>
        <span class="subheading">
          Вы действительно хотите принять сотрудника
          <span class="d-inline-block">{{ shortName }}</span>
          обратно?
        </span>
      </v-card-title>
      <v-card-actions>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat @click.native="hireUser">Принять</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'UserFireDialog',
    props: ['shortName'],
    data () {
      return {
        dialog: false
      }
    },
    methods: {
      hireUser () {
        this.dialog = false
        this.$emit('hire')
      }
    }
  }
</script>
