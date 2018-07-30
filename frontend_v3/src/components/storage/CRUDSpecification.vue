<template>
  <v-dialog v-model="dialog" persistent max-width="1100px">
    <v-card>
      <v-card-text>
        <v-form v-model="valid">
          <projects-select :readonly="specificationApproved" label="Проект" v-model="specificationItem.project.id"
                           required ref="projectSelector"/>
          <table
            style="border-top: 2px solid #282828; border-left: 2px solid #282828; border-collapse: collapse; width: 100%">
            <tr>
              <td class="cell" style="width: 40%; height: 100%; max-height: 30px;" colspan="6" rowspan="2"></td>
              <td class="cell px-3" style="width: 60%; height: 100%; max-height: 30px;" colspan="4">
                <v-text-field :readonly="specificationApproved" placeholder="Шифр" v-model="specificationItem.pressmark"
                              :rules="nonEmptyField"/>
              </td>
            </tr>

            <tr>
              <td class="cell px-3" colspan="4" rowspan="2">
                <v-text-field :readonly="specificationApproved" placeholder="Название объекта"
                              v-model="specificationItem.objectName"
                              :rules="nonEmptyField"/>
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 5%; text-align: center; height: 100%; height: 40px;">Изм.
              </td>
              <td class="cell" style="width: 5%; text-align: center;">Кол. уч.
              </td>
              <td class="cell" style="width: 5%; text-align: center;">Лист
              </td>
              <td class="cell" style="width: 5%; text-align: center;">№ док.
              </td>
              <td class="cell" style="width: 10%; text-align: center;">Подпись
              </td>
              <td class="cell" style="width: 10%; text-align: center;">Дата
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%; padding: 0" colspan="2">
                Разработал
              </td>
              <td class="cell" @click="selectedWorkerMethod('0')" style="width: 10%; max-width: 30px;" colspan="2">
                <workers-select :readonly="specificationApproved" v-model="specificationItem.workersData[0].name"
                                hide-details class="ellipsis" style="height: 100%; max-height: 30px; padding: 0"
                                @getSignature="getSignature"
                                combobox/>
              </td>
              <td class="cell" style="width: 10%; max-width: 100px; padding: 0">
                <img v-if="imagesPath[0]" style="height: 100%; max-height: 30px" :src="imagesPath[0]"/>
              </td>
              <td class="cell" style="width: 10%">
                <v-text-field :readonly="specificationApproved" v-model="specificationItem.dates[0]" class="px-1"
                              hide-details mask="##.##"
                              style="padding: 0"/>
              </td>
              <td class="cell px-3" style="width: 30%; text-align: center" rowspan="3">
                <v-text-field :readonly="specificationApproved" placeholder="Название раздела"
                              v-model="specificationItem.sectionName"
                              :rules="nonEmptyField"/>
              </td>
              <td class="cell" style="width: 10%; text-align: center">
                Стадия
              </td>
              <td class="cell" style="width: 10%; text-align: center">
                Лист
              </td>
              <td class="cell" style="width: 10%; text-align: center">
                Листов
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%" colspan="2">
                Проверил
              </td>
              <td class="cell" @click="selectedWorkerMethod('1')" style="width: 10%; max-width: 30px;" colspan="2">
                <workers-select :readonly="specificationApproved" v-model="specificationItem.workersData[1].name"
                                @getSignature="getSignature" hide-details
                                class="ellipsis" style="height: 100%; max-height: 30px; padding: 0" combobox/>
              </td>
              <td class="cell" style="width: 10%; max-width: 100px; padding: 0">
                <img v-if="imagesPath[1]" style="height: 100%; max-height: 30px; padding: 0" :src="imagesPath[1]"/>
              </td>
              <td class="cell" style="width: 10%">
                <v-text-field :readonly="specificationApproved" v-model="specificationItem.dates[1]" class="px-1"
                              hide-details mask="##.##"
                              style="padding: 0"/>
              </td>
              <td class="cell px-3" style="width: 10%; text-align: center" rowspan="2">
                <v-text-field :readonly="specificationApproved" placeholder="Стадия" hide-details
                              v-model="specificationItem.state"
                              :rules="nonEmptyField"/>
              </td>
              <td class="cell" style="width: 10%; text-align: center" rowspan="2">1
              </td>
              <td class="cell" style="width: 10%; text-align: center" rowspan="2">
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%" colspan="2">

              </td>
              <td class="cell" style="width: 10%; max-width: 100px; height: 30px" colspan="2">
              </td>
              <td class="cell" style="width: 10%">
              </td>
              <td class="cell" style="width: 10%">
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%; max-width: 100px; height: 30px" colspan="2">
              </td>
              <td class="cell" style="width: 10%" colspan="2">
              </td>
              <td class="cell" style="width: 10%">
              </td>
              <td class="cell" style="width: 10%">
              </td>
              <td class="cell px-3" style="width: 30%; text-align: center" rowspan="3">
                <v-text-field :readonly="specificationApproved" placeholder="Название документа"
                              v-model="specificationItem.documentName"
                              :rules="nonEmptyField"/>
              </td>
              <td class="cell px-3" style="width: 30%; text-align: center" colspan="3" rowspan="3">
                <v-text-field :readonly="specificationApproved" placeholder="Организация"
                              v-model="specificationItem.organization"
                              :rules="nonEmptyField"/>
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%" colspan="2">
                Н. Контр
              </td>
              <td class="cell" @click="selectedWorkerMethod('2')" style="width: 10%; max-width: 30px;" colspan="2">
                <workers-select :readonly="specificationApproved" v-model="specificationItem.workersData[2].name"
                                @getSignature="getSignature" hide-details
                                class="ellipsis" style="height: 100%; max-height: 30px; padding: 0" combobox/>
              </td>
              <td class="cell" style="width: 10%; max-width: 100px;">
                <img v-if="imagesPath[2]" style="height: 100%; max-height: 30px" :src="imagesPath[2]"/>
              </td>
              <td class="cell" style="width: 10%">
                <v-text-field :readonly="specificationApproved" v-model="specificationItem.dates[2]" class="px-1"
                              hide-details mask="##.##"
                              style="padding: 0"/>
              </td>
            </tr>

            <tr>
              <td class="cell" style="width: 10%" colspan="2">
                ГИП
              </td>
              <td class="cell" @click="selectedWorkerMethod('3')" style="width: 10%; max-width: 30px;" colspan="2">
                <workers-select :readonly="specificationApproved" v-model="specificationItem.workersData[3].name"
                                @getSignature="getSignature" hide-details
                                class="ellipsis" style="height: 100%; max-height: 30px; padding: 0" combobox/>
              </td>
              <td class="cell" style="width: 10%; max-width: 100px;">
                <img v-if="imagesPath[3]" style="height: 100%; max-height: 30px" :src="imagesPath[3]"/>
              </td>
              <td class="cell" style="width: 10%">
                <v-text-field :readonly="specificationApproved" v-model="specificationItem.dates[3]" class="px-1"
                              hide-details mask="##.##"
                              style="padding: 0"/>
              </td>
            </tr>

          </table>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="closeDialog" :loading="loading">Отменить</v-btn>
        <v-btn flat @click="cloneSpecification" :loading="loading" v-if="specificationItem.id">Дублировать</v-btn>
        <v-btn flat @click="deleteSpecification" :loading="loading" v-if="specificationItem.id">Удалить</v-btn>
        <v-btn flat @click="saveSpecification" :loading="loading" v-if="!specificationApproved" :disabled="!valid">
          Сохранить
        </v-btn>
        <span :title="approvalTitle">
          <v-btn flat @click="approveSpecification" :loading="loading"
                 v-if="specificationItem.id && !specificationApproved" :disabled="!valid || !allPositionsApproved"
                 v-show="auth.user.id === specificationItem.projectGip">Утвердить</v-btn>
          <v-btn flat @click="createRequisit" :loading="loading" v-else
                 v-show="auth.user.id === specificationItem.projectGip">Создать заявку на закупку</v-btn>
        </span>
      </v-card-actions>
    </v-card>
    <create-application ref="createApplication"/>
  </v-dialog>
</template>

<script>
  import auth from '../../auth/auth'
  import gql from 'graphql-tag'
  import {
    createSpecification,
    changeSpecification,
    deleteSpecification,
    specificationsPositions,
    cloneSpecification,
    specificationApproved
  } from './query'
  import WorkersSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import CreateApplication from '../CreateApplication'

  export default {
    name: 'CRUDSpecification',
    components: {
      ProjectsSelect,
      WorkersSelect,
      CreateApplication
    },
    data () {
      return {
        auth: auth,
        crutch: false,
        hasSignature: false,
        allWorkers: [],
        imagesPath: [null, null, null, null],
        valid: false,
        dialog: false,
        loading: false,
        selectedWorkerPosition: null,
        specificationItem: {
          id: null,
          project: {
            id: null,
            number: null
          },
          projectGip: null,
          pressmark: null,
          documentName: null,
          objectName: null,
          organization: null,
          sectionName: null,
          state: null,
          dates: [null, null, null, null],
          workersData: [{id: null, name: null}, {id: null, name: null}, {id: null, name: null}, {id: null, name: null}]
        },
        allPositionsApproved: false,
        specificationApproved: false,
        approvalTitle: '',
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    apollo: {
      query: {
        query: gql`
          query($search: String) {
            allUsers(search: $search){
              id
              shortName
              funcRoles
              hasSignature
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.allWorkers = data.allUsers
          return null
        },
        variables () {
          return {
            search: this.searchUsers
          }
        }
      },
      query2: {
        query: specificationsPositions,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            filters: this.specificationItem.id
          }
        },
        update (data) {
          // Проверка все ли позиции спецификации проверены. Если нет - блокируем кнопку
          this.approvalTitle = ''
          const specificationsPositions = JSON.parse(JSON.stringify(data.specificationsPositions))
          const hasUnchecked = specificationsPositions.some(item => {
            if (item.goodKind) {
              return item.goodKind.new
            } else {
              return false
            }
          })
          if (hasUnchecked) {
            this.approvalTitle = 'В спецификации используются не утвержденные виды товаров'
          }
          this.allPositionsApproved = !hasUnchecked
          if (specificationsPositions.length === 0) {
            this.allPositionsApproved = false
            this.approvalTitle = 'Спецификация пуста!'
          }
        }
      }
    },
    methods: {
      openDialog (val) {
        this.imagesPath = [null, null, null, null]
        if (val) {
          this.specificationApproved = val.approved
          val.workersData = JSON.parse(JSON.parse(val.workersData))
          this.specificationItem = val
          this.specificationItem.projectGip = val.project.gip.id
          val.workersData.forEach(function (item, index) {
            let signature = this.allWorkers.filter(function (user) {
              if (user.id === item.id) {
                return user
              }
            })
            if (signature.length > 0) {
              if (signature[0].hasSignature) {
                this.imagesPath[index] = 'http://localhost:8000/static/' + item.id + '.jpg'
              }
            }
          }, this)
        } else {
          this.specificationItem = {
            id: null,
            project: {
              id: null
            },
            projectGip: null,
            pressmark: null,
            documentName: null,
            objectName: null,
            organization: null,
            sectionName: null,
            state: null,
            checkListWorkers: [],
            dates: [null, null, null, null],
            workersData: [{id: null, name: null}, {id: null, name: null}, {id: null, name: null}, {
              id: null,
              name: null
            }]
          }
        }
        this.dialog = true
      },
      closeDialog () {
        this.$emit('success')
        this.dialog = false
      },
      selectedWorkerMethod (val) {
        this.selectedWorkerPosition = val
      },
      getSignature (val) {
        let temp = JSON.parse(JSON.stringify(this.imagesPath))
        if (typeof val === 'object') {
          this.crutch = true
          this.hasSignature = val.hasSignature
          this.specificationItem.workersData[this.selectedWorkerPosition] = {
            id: val.id,
            name: val.shortName
          }
          if (this.hasSignature === true && temp[this.selectedWorkerPosition] !== 'http://localhost:8000/static/undefined.jpg') {
            temp[this.selectedWorkerPosition] = 'http://localhost:8000/static/' + val.id + '.jpg'
          } else {
            temp[this.selectedWorkerPosition] = null
          }
        } else {
          if (this.crutch) {
            this.crutch = false
          } else {
            this.hasSignature = false
            this.specificationItem.workersData[this.selectedWorkerPosition] = {
              id: null,
              name: val
            }
            temp[this.selectedWorkerPosition] = null
          }
        }
        this.imagesPath = temp
      },
      saveSpecification () {
        setTimeout(() => {
          this.loading = true
          let workersData = JSON.stringify(this.specificationItem.workersData)
          // Если редактируем существующую спецификацию
          if (this.specificationItem.id) {
            // if (typeof this.specificationItem.project === 'object') {
            //   this.specificationItem.project = this.specificationItem.project.id
            // }
            this.$apollo.mutate({
              mutation: changeSpecification,
              variables: {
                input: {
                  id: this.specificationItem.id,
                  project: this.specificationItem.project.id,
                  pressmark: this.specificationItem.pressmark,
                  documentName: this.specificationItem.documentName,
                  objectName: this.specificationItem.objectName,
                  organization: this.specificationItem.organization,
                  sectionName: this.specificationItem.sectionName,
                  state: this.specificationItem.state,
                  workersData: workersData,
                  dates: this.specificationItem.dates
                }
              }
            }).then(() => {
              this.loading = false
              this.closeDialog()
              this.$emit('success')
            }).catch(() => {
              this.loading = false
            })
            // Если создаём новую спецификацию
          } else {
            this.$apollo.mutate({
              mutation: createSpecification,
              variables: {
                input: {
                  project: this.specificationItem.project.id,
                  pressmark: this.specificationItem.pressmark,
                  documentName: this.specificationItem.documentName,
                  objectName: this.specificationItem.objectName,
                  organization: this.specificationItem.organization,
                  sectionName: this.specificationItem.sectionName,
                  state: this.specificationItem.state,
                  workersData: workersData,
                  dates: this.specificationItem.dates
                }
              }
            }).then(() => {
              this.loading = false
              this.closeDialog()
              this.$emit('success')
            }).catch(() => {
              this.loading = false
            })
          }
        }, 100)
      },
      deleteSpecification () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deleteSpecification,
          variables: {
            input: {
              id: this.specificationItem.id
            }
          }
        }).then(() => {
          this.loading = false
          this.closeDialog()
          this.$emit('success')
          this.$router.push({name: 'specification'})
        }).catch(() => {
          this.loading = false
        })
      },
      approveSpecification () {
        this.loading = true
        this.$apollo.mutate({
          mutation: specificationApproved,
          variables: {
            input: {
              idSpec: this.specificationItem.id
            }
          }
        }).then(() => {
          this.loading = false
          this.specificationApproved = true
          // this.closeDialog()
          this.$emit('success')
        }).catch(() => {
          this.loading = false
        })
      },
      createRequisit () {
        this.$refs.createApplication.openDialog(this.specificationItem)
      },
      cloneSpecification () {
        this.loading = true
        this.$apollo.mutate({
          mutation: cloneSpecification,
          variables: {
            input: {
              idSpec: this.specificationItem.id
            }
          }
        }).then(({data}) => {
          if (data.cloneSpecification) {
            this.loading = false
            this.closeDialog()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Спецификация сдублирована'
            })
            this.$emit('success')
            this.$emit('reopen', data.cloneSpecification.result)
          }
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      'specificationItem.project.id': function (val) {
        if (this.specificationItem) {
          const project = this.$refs.projectSelector.allProjectsData.find(i => i.id === val)
          if (project) {
            this.specificationItem.project = project
          }
        }
      }
    }
  }
</script>

<style>
  img {
    width: 100%;
    height: 100%;
  }

  .cell {
    border-bottom: 2px solid #282828;
    border-right: 2px solid #282828;
  }
</style>
