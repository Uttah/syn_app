<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="500px">
    <v-card>
      <v-card-title>
        <span class="title">Изменение премии или вычета</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <workers-select label="Сотрудник" v-model="input.user" :disabled="disabled" required/>
              </v-flex>
              <v-flex xs12>
                <projects-select label="Проект" v-model="input.project" :disabled="disabled" required/>
              </v-flex>
              <v-flex xs6 class="pr-2">
                <integer-field label="Сумма" v-model="input.amount" :disabled="disabled" required :suffix="'руб.'"
                               :rules="amountValid"/>
              </v-flex>
              <v-flex xs6 class="pl-5 pt-3">
                <v-checkbox label="Наличными" v-model="input.cash"/>
              </v-flex>
              <v-flex xs12>
                <integer-field label="Рассрочка" v-model="input.installments" :disabled="disabled" :suffix="'мес.'"
                               required/>
              </v-flex>
              <v-flex xs12>
                <v-text-field label="Описание" v-model="input.description" :disabled="disabled" multiLine required
                              :rules="nonEmptyField"/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="disabled || loading" @click.native="deleteBonus" :loading="loading">Удалить</v-btn>
        <v-btn flat :disabled="!valid || disabled || loading" @click.native="updateBonus" :loading="loading">Обновить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import WorkersSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import auth from '../../auth/auth'
  import {deleteBonus, updateBonus} from './query'
  import IntegerField from '../IntegerField'

  export default {
    name: 'UpdateDeleteBonusDialog',
    props: [
      'input'
    ],
    components: {
      IntegerField,
      WorkersSelect,
      ProjectsSelect
    },
    data () {
      return {
        dialog: false,
        valid: false,
        disabled: false,
        loading: false,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        amountValid: [
          text => {
            const int = parseInt(text)
            if (int > 0 && auth.id !== 5) {
              return 'Вы можете устанавливать только отрицательные суммы'
            }
            return true
          }
        ]
      }
    },
    watch: {
      input: function () {
        this.dialog = true
        this.disabled = (auth.user.id !== this.input.userAdded.id && !auth.hasPermission('users.edit_all_bonuses')) || this.input.counted
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      deleteBonus () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: deleteBonus,
            variables: {
              input: {id: this.input.id}
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.deleteBonus.result === true) {
            this.dialog = false
            this.$emit('deleted')
          }
        }).catch(() => {
          this.loading = false
        })
      },
      updateBonus () {
        this.loading = true
        let input = {}
        input.id = this.input.id
        input.userId = (this.input.user && this.input.user.id) ? this.input.user.id : this.input.user
        input.projectId = (this.input.project && this.input.project.id) ? this.input.project.id : this.input.project
        input.amount = this.input.amount
        input.cash = this.input.cash
        input.installments = this.input.installments
        input.description = this.input.description
        this.$apollo.mutate(
          {
            mutation: updateBonus,
            variables: {
              input: input
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.updateBonus.bonus.id) {
            this.dialog = false
            this.$emit('updated')
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
