<template>
  <v-form ref="form" v-model="validInner" @submit.prevent="submit">
    <v-container class="pa-0">
      <v-layout wrap justify-center>
        <v-flex xs4 class="pr-3">
          <workers-select v-model="report.worker" label="Исполнитель" required :readonly="disabled"
                          @input="changeWorker" ref="workerInput" @loading-done="changeWorker"/>
        </v-flex>
        <v-flex xs4 class="px-3">
          <date-picker
            label="Дата"
            required
            :allowed-dates="allowedReportDates"
            v-model="report.reportDate"
            :rules="nonEmptyField"
            :readonly="disabled"
          />
        </v-flex>
        <v-flex xs4 class="pl-3">
          <v-select
            label="Функциональная роль"
            required
            :readonly="disabled && disabledEndMonth"
            :rules="nonEmptyField"
            v-model="report.funcRole"
            :items="funcRolesData"
            item-text="name"
            item-value="id"
          />
        </v-flex>
        <v-flex xs4 class="pr-3" :xs12="!showProcessSubProcess">
          <projects-select v-model="report.projects" single-gip label="Номер проекта" multiple required
                           :readonly="disabled"/>
        </v-flex>
        <v-flex xs4 class="px-3" v-if="showProcessSubProcess">
          <v-select
            label="Процесс"
            required
            :readonly="disabled && disabledEndMonth"
            :rules="nonEmptyField"
            v-model="report.process"
            :items="allProcessesData"
            item-text="name"
            item-value="id"
            @input="selectFirstSubProcess"
          />
        </v-flex>
        <v-flex xs4 class="pl-3" v-if="showProcessSubProcess">
          <v-select
            label="Подпроцесс"
            required
            :readonly="disabled && disabledEndMonth"
            :rules="nonEmptyField"
            v-model="report.subProcess"
            :items="allSubProcesses"
            item-text="name"
            item-value="id"
            @input="forceValidate"
          />
        </v-flex>
        <v-flex xs12 v-show="showTasks">
          <tasks-select :projects="report.projects" v-model="report.tasks" @show="showTasksMethod"
                        clearable/>
        </v-flex>
        <v-flex xs12 v-show="showTask">
          <v-text-field
            :label="taskLabel"
            multiLine
            :readonly="disabled"
            :rules="taskValid"
            v-model="report.task"
          />
        </v-flex>
        <v-flex xs4 class="pr-3" v-show="showDriving">
          <float-field label="Расстояние" v-model="report.distance" :required="showDriving"
                       :readonly="disabled" suffix="км"/>
        </v-flex>
        <v-flex xs4 class="pl-5 pr-3" v-show="showDriving">
          <v-radio-group label="Автомобиль" v-model="report.car" row :rules="drivingValid">
            <v-radio :readonly="disabled" label="Служебный" value="D"/>
            <v-radio :readonly="disabled" label="Личный" value="P"/>
          </v-radio-group>
        </v-flex>
        <v-flex xs4 class="pl-5" v-show="showDriving">
          <v-radio-group label="Бензин" v-model="report.gas" row :rules="drivingValid">
            <v-radio :readonly="disabled" label="По карте" value="D"/>
            <v-radio :readonly="disabled" label="Свой" value="P"/>
          </v-radio-group>
        </v-flex>
        <v-flex xs5 v-show="showDriving">
          <v-text-field
            label="Адрес отправления"
            :readonly="disabled"
            :rules="drivingValid"
            v-model="report.whereFrom"
          />
        </v-flex>
        <v-flex xs1 v-show="showDriving" class="text-xs-center">
          <v-btn :readonly="disabled" icon @click="replaceWhere" title="Поменять адреса местами" class="mt-3">
            <v-icon>mdi-swap-horizontal</v-icon>
          </v-btn>
        </v-flex>
        <v-flex xs5 v-show="showDriving">
          <v-text-field
            label="Адрес назначения"
            :readonly="disabled"
            :rules="drivingValid"
            v-model="report.whereTo"
          />
        </v-flex>
        <v-flex xs6 v-show="showArticle" class="pr-3">
          <v-text-field
            label="Артикул"
            :readonly="disabled"
            v-model="article"
            :rules="articleValid"
            mask="####.##"
            return-masked-value
          />
        </v-flex>
        <v-flex xs6 v-show="showSerialNumber" class="pr-3">
          <v-text-field
            label="Серийный номер"
            v-model="serialNumber"
            :rules="serialValid"
            :readonly="disabled"
            mask="####.##.###"
            return-masked-value
          />
        </v-flex>
        <v-flex xs6 v-show="showModel" class="pl-3">
          <v-text-field
            label="Модель"
            :readonly="disabled"
            v-model="report.model"
            :rules="modelValid"
          />
        </v-flex>
        <v-flex xs3>
          <time-input
            label="Затраченное время"
            prepend-icon="access_time"
            :readonly="disabled"
            v-model="timeSpentCalculation"
            required
          >
          </time-input>
        </v-flex>
        <v-flex xs6 class="mx-5">
          <v-card color="grey lighten-4">
            <v-layout>
              <v-flex xs3 class="mx-5">
                <time-picker :readonly="disabled" label="С" v-model="report.timeFrom" prepend-icon="access_time"
                             :rules="timeFromToRule"/>
              </v-flex>
              <v-flex xs3>
                <time-picker :readonly="disabled" label="По" v-model="report.timeTo" prepend-icon="access_time" @input="forceValidate"
                             :rules="timeFromToRule"/>
              </v-flex>
              <v-flex xs3>
                <v-checkbox label="Без обеда" v-model="withoutLunch" class="mt-3 ml-4"/>
              </v-flex>
            </v-layout>
          </v-card>
        </v-flex>

        <v-flex xs2 v-show="showNightShift">
          <v-checkbox :readonly="disabled" label="Ночная смена" v-model="report.nightShift" class="mt-3">
          </v-checkbox>
        </v-flex>
        <v-flex :xs12="!showMoneySpent" :xs6="showMoneySpent" :class="{'pr-3': showMoneySpent}">
          <v-select
            label="Место"
            required
            :readonly="disabled"
            v-model="report.place"
            :rules="nonEmptyField"
            :items="allPlacesData"
            item-text="name"
            item-value="id"
          />
        </v-flex>
        <v-flex xs6 class="pl-3" v-show="showMoneySpent">
          <integer-field label="Денег затрачено" v-model="report.moneySpent" :rules="moneyField"
                         :readonly="disabled"/>
        </v-flex>
        <v-flex xs6 class="pr-3" v-show="showQuality">
          <v-select label="Оценка качества" v-model="report.qualityGrade" :rules="qualityValid"
                    @input="forceValidate" :readonly="disabledQuality" :items="qualityGrades" clearable/>
        </v-flex>
        <v-flex xs6 class="pl-3" v-show="showQuality">
          <v-select label="Оценка срока" v-model="report.timeGrade" :rules="qualityValid" @input="forceValidate"
                    :readonly="disabledQuality" :items="timeGrades" clearable/>
        </v-flex>
        <v-flex xs12 v-show="showQuality">
          <v-text-field label="Комментарий" multiLine v-model="report.comment" :rules="commentValid"
                        :readonly="disabledQuality"/>
        </v-flex>
      </v-layout>
    </v-container>
  </v-form>
</template>


<script>
  import DatePicker from '../DatePicker.vue'
  import WorkersSelect from '../WorkersSelect.vue'
  import ProjectsSelect from '../ProjectsSelect.vue'
  import FloatField from '../FloatField.vue'
  import TimeInput from '../TimeInput'
  import {allForFill} from '../reports/query'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import TimePicker from '../TimePicker'
  import IntegerField from '../IntegerField'
  import TasksSelect from '../TasksSelect'

  export default {
    name: 'ReportDialog',
    mixins: [utilMixin],
    props: {
      reportGet: null,
      valid: Boolean,
      disabled: Boolean,
      disabledQuality: Boolean,
      disabledEndMonth: Boolean,
      gipId: {
        type: Number,
        default: null
      }
    },
    components: {
      IntegerField,
      TimePicker,
      WorkersSelect,
      ProjectsSelect,
      FloatField,
      DatePicker,
      TimeInput,
      TasksSelect
    },
    apollo: {
      query: {
        query: allForFill,
        update (data) {
          this.allFuncRolesData = data.allFuncRoles
          this.allProcessesData = data.allProcesses
          this.allPlacesData = data.allPlaces
          return null
        }
      }
    },
    data () {
      return {
        taskLabel: 'Задача',
        dialog: false,
        showTasks: false,
        validInner: this.valid,
        report: this.reportGet,
        allFuncRolesData: [],
        allProcessesData: [],
        allPlacesData: [],
        withoutLunch: false,
        timeFromToRule: [
          text => {
            if (this.report.timeFrom > this.report.timeTo) {
              return 'Дата "С" больше даты "По"'
            }
            return true
          }
        ],
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        nonEmptyArrayField: [
          array => array.length > 0 || 'Поле не может быть пустым'
        ],
        timeValid: [
          text => this.nonEmptyField[0](text),
          text => {
            if (text) {
              const tens = Number(text.slice(0, 2))
              const units = Number(text.slice(3, 5))
              if (tens > 23 || units > 59) {
                return 'Некорректное время'
              }
            }
            return true
          }
        ],
        serialValid: [
          text => {
            if (text.indexOf('.') > -1) {
              if (text.length === 11 || !this.showSerialNumber) {
                return true
              }
            } else {
              if (text.length === 9 || !this.showSerialNumber) {
                return true
              }
            }
            return 'Номер должен состоять из 9 цифр'
          }
        ],
        articleValid: [
          text => {
            if (text.indexOf('.') > -1) {
              if (text.length === 7 || !this.showArticle) {
                return true
              }
            } else {
              if (text.length === 6 || !this.showArticle) {
                return true
              }
            }
            return 'Номер должен состоять из 6 цифр'
          }
        ],
        taskValid: [
          text => {
            if (text || !this.showTask) {
              return true
            }
            return 'Поле не может быть пустым'
          }
        ],
        modelValid: [
          text => {
            if (text || !this.showModel) {
              return true
            }
            return 'Поле не может быть пустым'
          }
        ],
        drivingValid: [
          text => {
            if (text || !this.showDriving) {
              return true
            }
            return 'Поле не может быть пустым'
          }
        ],
        qualityValid: [
          text => {
            if ((this.checkGrade(this.report.qualityGrade) && !this.checkGrade(this.report.timeGrade)) ||
              (!this.checkGrade(this.report.qualityGrade) && this.checkGrade(this.report.timeGrade))) {
              return 'Для начисления коэффициента нужны обе оценки'
            }
            return true
          }
        ],
        commentValid: [
          text => {
            if (this.checkGrade(this.report.qualityGrade) &&
              this.checkGrade(this.report.timeGrade) && !this.report.comment) {
              return 'Поле не может быть пустым'
            }
            return true
          }
        ],
        allowedReportDates: function (date) {
          date = new Date(date)
          const now = new Date()
          return date < now
        },
        moneyField: [
          amount => {
            if (!amount) {
              return true
            } else if (amount >= 50) {
              return true
            } else {
              return 'Затраты должны быть больше 50 руб. При затратах меньше 50 руб. оставьте пустым'
            }
          }
        ],
        qualityGrades: [
          {text: '2 - неудовлетворительно (требуется переделка)', value: 2},
          {text: '3 - удовлетворительно (нет времени или возможности переделать)', value: 3},
          {text: '4 - хорошо (работа сделана приемлемо)', value: 4},
          {text: '5 - отлично (выше ожиданий)', value: 5}
        ],
        timeGrades: [
          {text: '0 - срока не было', value: 0},
          {text: '2 - не выполнено, либо срок провален', value: 2},
          {text: '3 - не успел по объективным причинам (либо были переделки)', value: 3},
          {text: '4 - успел в срок, без переделок', value: 4},
          {text: '5 - успел с опережением, без переделок', value: 5}
        ],
        selectedWorker: null
      }
    },
    methods: {
      checkGrade (grade) {
        if (grade === null) {
          return false
        } else {
          const int = parseInt(grade)
          return !isNaN(int) && int >= 0 && int <= 5
        }
      },
      replaceWhere () {
        const whereFrom = this.report.whereFrom
        const whereTo = this.report.whereTo
        this.report.whereFrom = whereTo
        this.report.whereTo = whereFrom
      },
      forceValidate () {
        this.$nextTick(() => this.$refs.form.validate())
      },
      selectFirstSubProcess () {
        this.$nextTick(() => {
          const process = this.allProcessesData.find(item => item.id === this.report.process)
          this.report.subProcess = process.subprocessSet[0].id
          this.forceValidate()
        })
      },
      changeWorker (newValue) {
        if (this.$refs.workerInput) {
          if (!newValue) {
            newValue = this.report.worker
          }
          const allUsers = this.$refs.workerInput.allUsersData
          if (allUsers.length > 0) {
            this.selectedWorker = allUsers.find(item => Number(item.id) === Number(newValue))
          }
        }
      },
      showTasksMethod (val) {
        this.showTasks = val
      }
    },
    computed: {
      funcRolesData () {
        if (this.selectedWorker) {
          const allowedFuncRoles = this.selectedWorker.funcRoles
          if (allowedFuncRoles && Array.isArray(allowedFuncRoles)) {
            const result = this.allFuncRolesData.filter(item => allowedFuncRoles.find(roleId => Number(item.id) === roleId))
            if (result.findIndex(item => item.id === this.report.funcRole) < 0 && result.length > 0) {
              this.report.funcRole = null
            }
            return result
          } else {
            return []
          }
        } else {
          return []
        }
      },
      allSubProcesses () {
        const process = this.allProcessesData.find(item => item.id === this.report.process)
        return process ? process.subprocessSet : []
      },
      showProcessSubProcess () {
        const place = this.allPlacesData.find(item => item.id === this.report.place)
        return place ? place.kind !== 'N' : true
      },
      showTask () {
        const SubProcess = this.allSubProcesses.find(item => item.id === this.report.subProcess)
        return SubProcess ? SubProcess.kind !== 'D' : false
      },
      showDriving () {
        const SubProcess = this.allSubProcesses.find(item => item.id === this.report.subProcess)
        return SubProcess ? SubProcess.kind === 'D' : false
      },
      showArticle () {
        const SubProcess = this.allSubProcesses.find(item => item.id === this.report.subProcess)
        return SubProcess ? SubProcess.kind === 'P' : false
      },
      showSerialNumber () {
        const SubProcess = this.allSubProcesses.find(item => item.id === this.report.subProcess)
        return SubProcess ? SubProcess.kind === 'A' : false
      },
      showModel () {
        const SubProcess = this.allSubProcesses.find(item => item.id === this.report.subProcess)
        return SubProcess ? (SubProcess.kind === 'A' || SubProcess.kind === 'P') : false
      },
      showMoneySpent () {
        const place = this.allPlacesData.find(item => item.id === this.report.place)
        return place ? place.kind === 'C' : false
      },
      showNightShift () {
        const process = this.allProcessesData.find(item => item.id === this.report.process)
        return process ? process.kind === 'N' : false
      },
      showQuality () {
        const funcRole = this.allFuncRolesData.find(item => item.id === this.report.funcRole)
        // return funcRole ? funcRole.kind === 'W' && auth.user.id !== this.report.worker : false
        let workerId = null
        if (this.report.worker && typeof this.report.worker === 'object') {
          workerId = this.report.worker.id
        } else {
          workerId = this.report.worker
        }
        const canManage = this.gipId && (this.gipId === auth.user.id || auth.hasPermission('reports.global_manage'))
        if (canManage) {
          return auth.user.id !== workerId
        } else {
          const result = funcRole && funcRole.kind === 'W' && auth.user.id !== workerId && !this.gipId
          if (this.report.userAdded) {
            return result && this.report.userAdded.id === auth.user.id
          } else {
            return result
          }
        }
      },
      timeSpentCalculation: {
        get: function () {
          if (this.report.timeFrom && this.report.timeTo) {
            if (this.report.timeFrom < this.report.timeTo) {
              const timeFrom = new Date(0)
              const timeTo = new Date(0)
              const timeFromArray = this.report.timeFrom.split(':')
              const timeToArray = this.report.timeTo.split(':')
              if (Number(timeFromArray[0]) * 60 + Number(timeFromArray[1]) <= Number(timeToArray[0]) * 60 + Number(timeToArray[1]) - 60) {
                this.withoutLunch ? timeTo.setHours(timeToArray[0]) : timeTo.setHours(timeToArray[0] - 1)
              } else {
                timeTo.setHours(timeToArray[0])
              }
              timeFrom.setHours(timeFromArray[0])
              timeFrom.setMinutes(timeFromArray[1])
              timeTo.setMinutes(timeToArray[1])
              const timeSpent = (timeTo - timeFrom) / 60000
              this.report.timeSpent = this.pad(Math.floor(timeSpent / 60), 2) + ':' + this.pad(timeSpent % 60, 2)
              return this.report.timeSpent
            } else {
              return this.report.timeSpent
            }
          } else {
            return this.report.timeSpent
          }
        },
        set: function (text) {
          this.report.timeSpent = text
          this.report.timeFrom = null
          this.report.timeTo = null
        }
      },
      article: {
        get: function () {
          return this.pad(this.report.vcProject, 4) + '' + this.pad(this.report.vcDigits, 2)
        },
        set: function (text) {
          if (text.length === 7) {
            const objects = text.split('.')
            this.report.vcProject = objects[0]
            this.report.vcDigits = objects[1]
          }
        }
      },
      serialNumber: {
        get: function () {
          return this.pad(this.report.vcProject, 4) + '' + this.pad(this.report.vcDigits, 2) + '' +
            (this.report.vcDigitsMinor ? this.pad(this.report.vcDigitsMinor, 3) : '')
        },
        set: function (text) {
          if (text.length === 11) {
            const objects = text.split('.')
            this.report.vcProject = objects[0]
            this.report.vcDigits = objects[1]
            this.report.vcDigitsMinor = objects[2]
          }
        }
      }
    },
    watch: {
      showTasks: function (val) {
        if (val) {
          this.taskLabel = 'Что было сделано'
        } else {
          this.taskLabel = 'Задача'
        }
      },
      reportGet: function (val) {
        if (val) {
          if (val.timeTo && val.timeFrom) {
            let timeToArray = val.timeTo.split(':')
            let timeFromArray = val.timeFrom.split(':')
            let timeSpentArray = val.timeSpent.split(':')
            let timeTo = new Date(0)
            let timeFrom = new Date(0)
            let timeSpent = new Date(0)
            let newDate = new Date(0)
            timeTo.setHours(timeToArray[0])
            timeTo.setMinutes(timeToArray[1])
            timeFrom.setHours(timeFromArray[0])
            timeFrom.setMinutes(timeFromArray[1])
            timeSpent.setHours(timeSpentArray[0])
            timeSpent.setMinutes(timeSpentArray[1])
            newDate.setHours('00')
            newDate.setMinutes('00')
            if ((timeTo - timeFrom) / 60000 === (timeSpent - newDate) / 60000) {
              this.withoutLunch = true
            }
          }
          this.report = val
        }
      },
      validInner: function (val) {
        this.$emit('update:valid', val)
      },
      report: {
        handler: function (val) {
          const SubProcess = this.allSubProcesses.find(item => item.id === val.subProcess)
          if (SubProcess && SubProcess.kind === 'D') {
            val.vcProject = null
            val.vcDigits = null
            val.vcDigitsMinor = null
            val.task = null
            val.model = null
          }
          if (SubProcess && SubProcess.kind === 'P') {
            val.vcDigitsMinor = null
          }
          if (SubProcess && SubProcess.kind !== 'D') {
            val.distance = null
            val.car = null
            val.gas = null
            val.whereTo = null
            val.whereFrom = null
          }
          const places = this.allPlacesData.find(item => item.id === val.place)
          if (places && places.kind !== 'C' && places.kind !== 'N') {
            val.moneySpent = null
          }
          if (places && places.kind === 'N') {
            val.process = null
            val.subProcess = null
          }
          const funcRole = this.allFuncRolesData.find(item => item.id === val.funcRole)
          const canManage = this.gipId && (this.gipId === auth.user.id || auth.hasPermission('reports.global_manage'))
          let workerId = null
          if (this.report.worker && typeof this.report.worker === 'object') {
            workerId = this.report.worker.id
          } else {
            workerId = this.report.worker
          }
          if (canManage) {
            if (auth.user.id === workerId) {
              val.qualityGrade = null
              val.timeGrade = null
              val.comment = null
            }
          } else {
            if (!(funcRole && funcRole.kind === 'W' && auth.user.id !== workerId)) {
              val.qualityGrade = null
              val.timeGrade = null
              val.comment = null
            }
          }
          const process = this.allProcessesData.find(item => item.id === val.process)
          if (process) {
            if (process.kind !== 'N') {
              val.nightShift = false
            }
          }
          this.$emit('update:reportGet', val)
        },
        deep: true
      }
    }
  }
</script>

<style scoped>
  .container .layout .flex {
    padding: 0;
  }
</style>
