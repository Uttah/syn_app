<template>
  <v-dialog v-model="dialog" persistent max-width="500px" lazy>
    <template slot="activator">
      <slot name="activator"/>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Смена пароля</span>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs10 offset-xs1>
              <v-text-field label="Новый пароль" required v-model="newPassword" type="password"
                            name="newPassword" :rules="passwordRule"/>
            </v-flex>
            <v-flex xs10 offset-xs1>
              <v-text-field label="Ввод еще раз" required v-model="confirmation" type="password"
                            name="confirmation" :rules="passwordRule"/>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <span class="subheading ml-3 error--text" v-if="!passwordsMatch">Пароли не совпадают</span>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!passwordsMatch" @click.native="save">Сменить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'UserPasswordDialog',
    data () {
      return {
        dialog: false,
        newPassword: '',
        confirmation: '',
        passwordRule: [
          text => !!text || 'Пароль не может быть пустым',
          text => text.length >= 8 || 'Минимум 8 символов'
        ]
      }
    },
    computed: {
      passwordsMatch () {
        return this.newPassword === this.confirmation && this.newPassword !== ''
      }
    },
    methods: {
      save () {
        this.dialog = false
        this.$emit('save', this.newPassword)
      }
    }
  }
</script>
