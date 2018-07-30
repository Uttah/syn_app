<template>
  <v-dialog v-model="dialog" persistent max-width="750px" lazy>
    <v-btn color="submit" slot="activator" class="ml-3">Добавить отсутствие</v-btn>
    <v-card>
      <v-card-title>
        <span class="headline">{{ editing ? 'Редактирование' : 'Добавление' }} отсутствия сотрудника</span>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form v-model="valid" ref="form">
          <v-container grid-list-md>
            <v-layout row wrap justify-space-around>
              <v-flex xs11>
                <workers-select label="Отсутствующий" v-model="innerAbsence.worker" required :subordinate="!auth.hasPermission('absences.add_absence')"/>
              </v-flex>
              <v-flex xs11>
                <v-radio-group label="Время отсутствия" v-model="dateKind" row class="pa-0 ma-0">
                  <v-radio label="Один день" value="D"/>
                  <v-radio label="Период" value="P"/>
                </v-radio-group>
              </v-flex>
              <v-flex xs5>
                <date-picker :label="beginLabel" v-model="innerAbsence.begin" required
                             :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs5 v-if="dateKind === 'P'">
                <date-picker label="Дата окончания" v-model="innerAbsence.end" :required="dateKind === 'P'"
                             :rules="nonEmptyPField" @focus="calcFocused = true; workDays = null"
                             @input="val => {if (val) {this.calcFocused = false} }"/>
              </v-flex>
              <v-flex xs5 v-show="dateKind === 'P'">
                <integer-field label="Рабочих дней" v-model="workDays"
                               @focus="calcFocused = true; innerAbsence.end = null"
                               @blur="calcFocused = false"/>
              </v-flex>
              <v-flex xs5 v-show="dateKind === 'P'">
                <integer-field label="Календарных дней" v-model="days" readonly/>
              </v-flex>
              <v-flex xs5 v-show="dateKind === 'D'">
                <time-input label="Учтенное время" prepend-icon="access_time" :required="dateKind === 'D'"
                            v-model="innerAbsence.time"/>
              </v-flex>
              <v-flex xs11>
                <absence-reason-picker label="Причина отсутствия" v-model="innerAbsence.reason" required
                                       :readonly="!auth.hasPermission('absences.change_reason')">
                </absence-reason-picker>
              </v-flex>
              <v-flex xs11>
                <v-text-field label="Комментарий" v-model="innerAbsence.comment"/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false" :disabled="innerDisable">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!valid || innerDisable" @click.native="remove"
               :loading="innerDisable" v-if="editing">Удалить</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!valid || innerDisable" @click.native="save"
               :loading="innerDisable">Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import WorkersSelect from '../WorkersSelect'
  import AbsenceReasonPicker from './AbsenceReasonPicker'
  import DatePicker from '../DatePicker'
  import auth from '../../auth/auth'
  import moment from 'moment'
  import IntegerField from '../IntegerField'
  import TimeInput from '../TimeInput'
  import {absenceWorkingDays} from './query'

  export default {
    components: {
      TimeInput,
      IntegerField,
      AbsenceReasonPicker,
      WorkersSelect,
      DatePicker
    },
    name: 'absence-edit-dialog',
    props: {
      disableButtons: Boolean
    },
    apollo: {
      query: {
        query: absenceWorkingDays,
        variables () {
          return {
            begin: this.innerAbsence.begin,
            end: this.innerAbsence.end,
            workingDays: this.workDays
          }
        },
        update (data) {
          if (data && data.absenceWorkingDays) {
            if (data.absenceWorkingDays.end) {
              this.innerAbsence.end = data.absenceWorkingDays.end
            } else {
              if (data.absenceWorkingDays.workingDays) {
                this.workDays = data.absenceWorkingDays.workingDays
              }
            }
          }
        },
        skip () {
          return !this.innerAbsence.begin || (this.innerAbsence.end && this.workDays) || (!this.innerAbsence.end && !this.workDays) || this.calcFocused
        }
      }
    },
    data () {
      return {
        dialog: false,
        valid: false,
        calcFocused: false,
        innerDisable: this.disableButtons,
        innerAbsence: {
          begin: null,
          end: null,
          worker: null,
          reason: null
        },
        dk: null,
        nonEmptyPField: [
          text => {
            if (this.dateKind === 'D') {
              return true
            } else {
              return !!text || 'Поле не может быть пустым'
            }
          }
        ],
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        editing: false,
        initialFill: false,
        workDays: null,
        auth: auth
      }
    },
    computed: {
      dateKind: {
        get () {
          if (this.dk === null) {
            this.dk = (this.innerAbsence.begin === this.innerAbsence.end) ? 'D' : 'P'
          }
          return this.dk
        },
        set (newValue) {
          this.dk = newValue
          if (this.dk === 'P') {
            this.innerAbsence.time = '08:00'
          } else {
            this.innerAbsence.end = this.innerAbsence.begin
          }
        }
      },
      beginLabel () {
        return this.dateKind === 'D' ? 'Дата' : 'Дата начала'
      },
      days: {
        set (newValue) {
          if (this.dateKind === 'P') {
            this.innerAbsence.end = moment(this.innerAbsence.begin).add(newValue - 1, 'd').format('Y-MM-DD')
          }
        },
        get () {
          if (this.innerAbsence.end && this.innerAbsence.begin) {
            return moment(this.innerAbsence.end).diff(moment(this.innerAbsence.begin), 'days') + 1
          } else {
            return 0
          }
        }
      }
    },
    watch: {
      dialog (newValue) {
        if (!newValue) {
          setTimeout(() => {
            this.editing = false
          }, 500)
        } else {
          if (!this.editing) {
            this.dk = null
            this.innerAbsence = {
              begin: null,
              end: null,
              worker: null,
              reason: null
            }
            if (!auth.hasPermission('absences.change_reason')) {
              this.innerAbsence.reason = '7'
            }
          }
        }
      },
      disableButtons (newVal) {
        if (!newVal && this.innerDisable && this.dialog) {
          this.dialog = false
        }
        this.innerDisable = newVal
      },
      'innerAbsence.begin': function (newVal) {
        // Не очищать поле конца интервала при первом заполнении
        if (!this.initialFill) {
          this.clearCalcFields()
        } else {
          this.workDays = null
          this.initialFill = false
        }
      }
    },
    methods: {
      show (item) {
        if (item) {
          this.innerAbsence = JSON.parse(JSON.stringify(item))
          this.innerAbsence.reason = item.reason.id
          this.innerAbsence.worker = item.worker.id
          this.dk = (this.innerAbsence.begin === this.innerAbsence.end) ? 'D' : 'P'
          this.editing = true
          this.dialog = true
          this.initialFill = true
        }
      },
      save () {
        this.$emit('update:disableButtons', true)
        if (this.editing) {
          this.$emit('save', this.innerAbsence)
        } else {
          if (this.dateKind === 'P') {
            this.innerAbsence.time = '08:00'
          } else {
            this.innerAbsence.end = this.innerAbsence.begin
          }
          this.$emit('add', this.innerAbsence)
        }
      },
      remove () {
        this.$emit('update:disableButtons', true)
        if (this.editing) {
          this.$emit('remove', this.innerAbsence)
        }
      },
      clearCalcFields () {
        this.innerAbsence.end = null
        this.workDays = null
      }
    }
  }
</script>
