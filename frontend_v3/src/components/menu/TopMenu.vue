<template>
  <v-toolbar dense color="toolbar">
    <v-toolbar-items class="hidden-sm-and-down">
      <template v-for="topItem in menuItems">
        <top-menu-item :menu-item="topItem" v-if="topItem.subItems.length"/>
      </template>
    </v-toolbar-items>
    <v-spacer/>
    <span class="subheader black--text">{{ greeting }}</span>
    <v-btn to="/help" icon title="Справочный раздел">
      <v-icon>help_outline</v-icon>
    </v-btn>
    <v-btn to="/my_salary" icon title="Зарплатная ведомость">
      <v-icon>attach_money</v-icon>
    </v-btn>
    <user-password-dialog @save="changePassword">
      <v-btn icon title="Сменить пароль" slot="activator">
        <v-icon>mdi-lock-reset</v-icon>
      </v-btn>
    </user-password-dialog>
    <v-btn to="/logout" icon title="Выход">
      <v-icon>exit_to_app</v-icon>
    </v-btn>
  </v-toolbar>
</template>

<script>
  import TopMenuItem from './TopMenuItem.vue'
  import auth from '../../auth/auth'
  import gql from 'graphql-tag'
  import UserPasswordDialog from '../user/PasswordDialog'

  export default {
    name: 'TopMenu',
    components: {
      UserPasswordDialog,
      TopMenuItem
    },
    apollo: {
      menuItems: {
        query: gql`{
          menuItems: menu {
            name: text,
            subItems: items {
              link,
              label: text
            }
          }
        }`,
        skip () {
          // Не запрашиваем меню если мы знаем, что не залогинены
          return auth.user.id < 1
        }
      }
    },
    data () {
      return {
        menuItems: []
      }
    },
    computed: {
      greeting () {
        if (auth.user.id < 1) {
          return ''
        } else {
          return 'Вы вошли как ' + auth.user.shortName
        }
      }
    },
    methods: {
      changePassword (password) {
        this.$apollo.mutate({
          mutation: gql`
            mutation ($input: ChangeOwnPasswordInput!) {
              changeOwnPassword(input: $input) {
                success
              }
            }
          `,
          variables: {
            input: {
              password: password
            }
          }
        })
      }
    }
  }
</script>
