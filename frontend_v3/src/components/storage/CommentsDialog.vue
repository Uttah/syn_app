<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <v-card>
      <v-card-title>
        <v-toolbar flat color="white">
          <span class="ma-0 headline">Комментарий</span>
        </v-toolbar>
      </v-card-title>
      <v-card-text>
        <v-text-field multi-line v-model="comment" readonly/>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="closeDialog">Отмена</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'CommentsDialog',
    data () {
      return {
        dialog: false,
        comment: ''
      }
    },
    methods: {
      openDialog (val) {
        this.dialog = true
        this.comment = val
      },
      closeDialog () {
        this.dialog = false
        this.comment = ''
      }
    }
  }
</script>

