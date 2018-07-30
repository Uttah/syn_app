<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Привязка должностей к пользователям</span>
        <v-spacer/>
        <v-dialog v-model="assignPositionDialog" persistent max-width="500">
          <v-btn v-if="auth.hasPermission('users.can_assign_position')" color="primary" dark slot="activator">Назначить
            должность
          </v-btn>
          <v-card>
            <v-form v-model="valid">
              <v-container>
                <v-layout wrap justify-center>
                  <v-flex xs12>
                    <workers-select label="Пользователь" required v-model="assignData.user"/>
                  </v-flex>
                  <v-flex xs12>
                    <v-select
                      label="Должности"
                      required
                      :items="positionsData"
                      item-text="name"
                      item-value="id"
                      v-model="assignData.position"
                      :rules="nonEmptyField"
                    >
                    </v-select>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-form>
            <v-card-actions>
              <v-spacer/>
              <v-btn flat :disabled="loading" @click.native="assignPositionDialog = false">
                Отмена
              </v-btn>
              <v-btn flat :disabled="!valid || loading" :loading="loading" @click.native="assignPositionFunc">
                Назначить
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-dialog v-model="removePositionDialog" max-width="500px">
          <v-card>
            <v-card-text>
              Вы действительно хотите снять {{itemToDelete.user}} с должности {{itemToDelete.position}}?
            </v-card-text>
            <v-card-actions>
              <v-spacer/>
              <v-btn flat :disabled="loading" @click.native="removePositionDialog = false">
                Отмена
              </v-btn>
              <v-btn flat :disabled="loading" :loading="loading" @click.native="removePositionFunc(itemToDelete)">
                Снять
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="allUsersAndPositionsData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
      style="max-width: 1000px"
      class="mx-auto"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td class="text-xs-center">{{ props.item.user }}</td>
          <td class="text-xs-center">{{ props.item.position }}</td>
          <td style="width: 20px;">
            <v-btn v-if="auth.hasPermission('users.can_remove_position')" icon @click="warnDelete(props.item)">
              <v-icon>delete</v-icon>
            </v-btn>
          </td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {allUsersAndPositions, assignPosition, removePosition} from './query'
  import {allCompanies} from '../financial_info/query'
  import WorkersSelect from '../WorkersSelect'
  import auth from '../../auth/auth'

  export default {
    components: {WorkersSelect},
    name: 'position-bind',
    metaInfo: {
      title: 'Привязка должностей к пользователям'
    },
    apollo: {
      fetchAllUsersAndPositionsData: {
        fetchPolicy: 'cache-and-network',
        query: allUsersAndPositions,
        update (data) {
          this.allUsersAndPositionsData = data.allUsersAndPositions
        },
        loadingKey: 'loadingQueriesCount'
      },
      fetchPositionData: {
        fetchPolicy: 'cache-and-network',
        query: allCompanies,
        update (data) {
          data.companies.forEach(company => {
            if (company.positionSet) {
              company.positionSet.forEach(position => {
                this.positionsData.push(
                  {
                    id: position.id,
                    name: `${company.shortName} - ${position.name}`
                  }
                )
              })
            }
          })
        }
      }
    },
    data () {
      return {
        auth: auth,
        assignPositionDialog: false,
        removePositionDialog: false,
        valid: false,
        allUsersAndPositionsData: [],
        positionsData: [],
        headers: [
          {text: 'Сотрудник', align: 'center', value: 'user', sortable: false},
          {text: 'Должность', align: 'center', value: 'position', sortable: false}
        ],
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0,
        loading: false,
        assignData: {
          user: null,
          position: null
        },
        itemToDelete: {
          user: null,
          position: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      assignPositionFunc () {
        this.loading = true
        this.$apollo.mutate({
          mutation: assignPosition,
          variables: {
            input: this.assignData
          }
        }).then(({data}) => {
          if (data.assignPosition.result) {
            this.assignPositionDialog = false
            this.loading = false
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Сотрудник назначен на должность'
            })
            this.$apollo.queries.fetchAllUsersAndPositionsData.refetch()
          }
        }).catch(() => {
          this.loading = false
        })
      },
      removePositionFunc (item) {
        this.loading = true
        this.$apollo.mutate({
          mutation: removePosition,
          variables: {
            input: {
              user: item.userId,
              position: item.positionId
            }
          }
        }).then(({data}) => {
          if (data.removePosition.result) {
            this.removePositionDialog = false
            this.loading = false
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Сотрудник снят с должности'
            })
            this.$apollo.queries.fetchAllUsersAndPositionsData.refetch()
          }
        })
      },
      warnDelete (item) {
        this.itemToDelete = item
        this.removePositionDialog = true
      }
    }
  }
</script>
