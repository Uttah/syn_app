<template>
  <v-dialog v-model="dialog" persistent max-width="500px" lazy>
    <v-btn color="submit" slot="activator" class="ml-3">Принять на должность</v-btn>
    <v-card>
      <v-card-title>
        <span class="headline">Приём сотрудника на должность</span>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form v-model="valid" ref="form">
          <v-container grid-list-md>
            <v-layout row wrap justify-space-around>
              <v-flex xs11>
                <workers-select label="Пользователь" v-model="pickedUser" required
                                :readonly="typeof user !== 'undefined'">
                </workers-select>
              </v-flex>
              <v-flex xs11>
                <v-select :items="companies" v-model="company" item-text="name" item-value="id" required
                          label="Компания" :loading="loadingCompanies > 0 ? 'loading' : false"
                          :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs11>
                <v-select :items="positions" v-model="position" item-text="name" item-value="id" required
                          label="Должность" :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs11>
                <v-checkbox label="Начисление з/п по коэффициентам" v-model="coefficients" hide-details>
                </v-checkbox>
              </v-flex>
              <v-flex xs11>
                <v-checkbox label="Почасовая оплата" v-model="byHours" :disabled="coefficients" hide-details>
                </v-checkbox>
              </v-flex>
              <v-flex xs5>
                <integer-field name="salary" label="Ставка (за 100%)" v-model="salary" suffix="руб."
                               :required="!coefficients" :disabled="coefficients" :rules="salaryRules"/>
              </v-flex>
              <v-flex xs5>
                <integer-field name="fraction" label="% ставки" v-model="fraction" suffix="%" required
                               :rules="positive"/>
              </v-flex>
              <v-flex xs5>
                <integer-field name="base" label="Оклад по договору" v-model="base" suffix="руб." required
                               :rules="positive"/>
              </v-flex>
              <v-flex xs5>
                <integer-field name="advance" label="Аванс" v-model="advance" suffix="руб." required
                               :rules="positive"/>
              </v-flex>
              <v-flex xs6>
                <date-picker name="hireDate" label="Дата приёма" v-model="hireDate" required
                             :rules="nonEmptyField"/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false" :disabled="loading">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!valid || loading" @click.native="save" :loading="loading">
          Принять
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {allCompanies, addPosition, positionsQuery} from './query'
  import DatePicker from '../DatePicker.vue'
  import WorkersSelect from '../WorkersSelect'
  import IntegerField from '../IntegerField'

  export default {
    name: 'PositionsHireDialog',
    components: {
      IntegerField,
      WorkersSelect,
      DatePicker
    },
    props: ['user'],
    apollo: {
      companies: {
        fetchPolicy: 'cache-and-network',
        query: allCompanies,
        loadingKey: 'loadingCompanies'
      }
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        company: null,
        position: null,
        pickedUser: this.user,
        companies: [],
        positions: [],
        loadingUsers: 0,
        loadingCompanies: 0,
        salary: 0,
        fraction: 100,
        base: 0,
        advance: 0,
        hireDate: null,
        byHours: false,
        coefficients: false,
        salaryRequired: true,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        positive: [
          text => text > 0 || 'Только положительные числа'
        ],
        salaryRules: [
          text => {
            if (this.coefficients) {
              return true
            }
            return this.positive[0](text)
          }
        ]
      }
    },
    watch: {
      company (newValue) {
        this.positions = this.companies.find(company => company.id === newValue).positions
      },
      user (newValue) {
        this.pickedUser = newValue
      },
      coefficients (newValue) {
        this.$nextTick(() => {
          this.$refs.form.validate()
          if (newValue) {
            this.byHours = true
            this.salary = null
          }
        })
      }
    },
    methods: {
      save () {
        this.loading = true
        this.$apollo.mutate({
          mutation: addPosition,
          variables: {
            input: {
              userId: this.pickedUser,
              positionId: this.position,
              byHours: this.byHours,
              hireDate: this.hireDate,
              salary: this.salary,
              base: this.base,
              advance: this.advance,
              fraction: this.fraction
            }
          },
          update: (store, {data: {addOccupation}}) => {
            // Обновляем кеш новой должностью
            const query = {query: positionsQuery, variables: {userId: this.pickedUser}}
            try {
              const data = store.readQuery(query)
              data.positions.push(addOccupation.occupation)
              query.data = data
              store.writeQuery(query)
            } catch (e) {
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.addOccupation.occupation) {
            this.$emit('hire')
            this.dialog = false
          }
        })
      }
    }
  }
</script>

<style>
  .container.grid-list-md .layout .flex {
    padding: 0;
  }
</style>
