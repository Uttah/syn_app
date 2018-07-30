<template>
  <v-toolbar flat color="white">
    <h5 class="headline ma-0 px-3" :class="{ fired: user.fired }">
      <v-btn to="/users" icon title="Назад к списку пользователей">
        <v-icon>arrow_back</v-icon>
      </v-btn>
      {{ user.fullName }}
      <span v-if="user.fired" class="grey--text text--darken-2">({{ firedTag }})</span>
    </h5>
    <v-spacer/>
    <fire-dialog v-if="canFire && !user.fired" v-model="fireDate"
                 :short-name="user.shortName" @fire="fire"/>
    <hire-dialog v-else-if="canFire" :short-name="user.shortName" @hire="$emit('hire')"/>
    <v-btn color="submit" @click="save" :disabled="!canSave">Сохранить</v-btn>
    <v-btn to="/users">Назад</v-btn>
  </v-toolbar>
</template>

<script>
  import auth from '../../auth/auth'
  import FireDialog from './FireDialog.vue'
  import HireDialog from './HireDialog.vue'
  import utilMixin from '../utils'

  export default {
    name: 'UserHeader',
    mixins: [utilMixin],
    props: ['user', 'firedTag', 'canSave'],
    components: {
      FireDialog,
      HireDialog
    },
    data () {
      return {
        fireDate: this.nowText
      }
    },
    computed: {
      canFire () {
        return auth.hasPermission('users.fire_user')
      },
      nowText () {
        const now = new Date()
        return now.toString()
      }
    },
    methods: {
      save () {
        this.$emit('save')
      },
      fire () {
        this.$emit('fire', this.fireDate)
      }
    }
  }
</script>
