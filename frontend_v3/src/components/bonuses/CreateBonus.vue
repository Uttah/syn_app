<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="500px">
    <v-btn color="primary" slot="activator">Создать премию или вычет</v-btn>
    <v-card>
      <v-card-title>
        <span class="title">Создание премии или вычета</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-center>
              <v-flex xs12>
                <workers-select label="Сотрудник" v-model="input.userId" required/>
              </v-flex>
              <v-flex xs12>
                <projects-select label="Проект" v-model="input.projectId" required/>
              </v-flex>
              <v-flex xs6 class="pr-2">
                <integer-field label="Сумма" v-model="input.amount" required :rules="amountValid" :suffix="'руб.'">
                </integer-field>
              </v-flex>
              <v-flex xs6 class="pl-5 pt-3">
                <v-checkbox label="Наличными" v-model="input.cash"/>
              </v-flex>
              <v-flex xs12>
                <integer-field label="Рассрочка" v-model="input.installments" required :suffix="'мес.'"/>
              </v-flex>
              <v-flex xs12>
                <v-text-field label="Описание" v-model="input.description" multiLine required :rules="nonEmptyField"/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="!valid || loading" @click.native="createBonus" :loading="loading">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import WorkersSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import {createBonus} from './query'
  import auth from '../../auth/auth'
  import IntegerField from '../IntegerField'

  export default {
    name: 'CreateBonusDialog',
    components: {
      IntegerField,
      WorkersSelect,
      ProjectsSelect
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        input: {
          userId: null,
          projectId: null,
          amount: null,
          cash: false,
          installments: 1,
          description: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        amountValid: [
          text => {
            const int = parseInt(text)
            if (int > 0 && auth.user.id !== 5) {
              return 'Вы можете устанавливать только отрицательные суммы'
            }
            return true
          }
        ]
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      createBonus () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createBonus,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.createBonus.bonus.id) {
            this.dialog = false
            this.$emit('created')
          }
        })
      }
    }
  }
</script>
