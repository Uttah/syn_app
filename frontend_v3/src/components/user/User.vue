<template>
  <v-card>
    <v-card-title>
      <v-progress-linear class="pa-0 ma-0" height="4" :indeterminate="true"
                         :active="loadingQueriesCount > 0"/>
      <user-header :user="user" :firedTag="firedTag" :canSave="valid" @save="saveUser" @fire="fireUser"
                   @hire="hireUser"/>
    </v-card-title>
    <v-card-text>
      <v-container fluid class="pa-0">
        <v-layout row class="d-flex">
          <avatar-upload :mutate="saveUserAvatar"
                         :variables="{userId: user.id}"
                         :extractPath="result => result.saveUserAvatar.imagePath"
                         v-model="user.avatar"
                         style="max-width: 300px" class="ml-5"
          />
          <v-form v-model="valid">
            <!-- Первая строка -->
            <v-layout row>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="lastName" label="Фамилия" v-model="user.lastName" required :rules="nonEmptyField"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="email" label="Электронная почта" prepend-icon="email" v-model="user.email"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex style="width: 16%; min-width: 100px">
                <date-picker v-model="user.birthDate" label="Дата рождения" :allowed-dates="allowedBirthDates"/>
              </v-flex>
              <v-flex style="width: 6%; min-width: 40px; padding-top: 21px; padding-left: 10px">
                <span class="subheading" style="vertical-align: baseline;" v-if="user.birthDate">({{age}})</span>
              </v-flex>
              <v-spacer class="spacer_width"/>
            </v-layout>
            <!-- Вторая строка -->
            <v-layout row>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="firstName" label="Имя" v-model="user.firstName" required :rules="nonEmptyField"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="workPhone" label="Рабочий телефон" prepend-icon="phone"
                              mask="8 (###) ###-##-##" v-model="user.workPhone"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width noIcon">
                <v-select label="Пол" :items="genderItems" v-model="user.gender"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
            </v-layout>
            <!-- Третья строка -->
            <v-layout row>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="patronym" label="Отчество" v-model="user.patronym"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="personalPhone" label="Личный телефон" prepend-icon="phone"
                              mask="8 (###) ###-##-##" v-model="user.personalPhone"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width noIcon">
                <v-checkbox class="pt-3" label="Не курит" v-model="user.healthy"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
            </v-layout>
            <!-- Четвертая строка -->
            <v-layout row>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <v-text-field name="login" label="Логин" v-model="user.login" :rules="nonEmptyField"
                              required/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <user-password-dialog class="pt-2" @save="changePassword">
                  <v-btn slot="activator">Сменить пароль</v-btn>
                </user-password-dialog>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width noIcon">
                <v-checkbox class="pt-3" label="Суперпользователь" @change="setSuperUser"
                            v-model="user.isSuperUser"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
            </v-layout>
            <!-- Пятая строка -->
            <v-layout row>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <date-picker v-model="user.hireDate" label="Дата приёма" required/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width">
                <date-picker v-model="user.fireDate" label="Дата увольнения" :disabled="!user.fired"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
              <v-flex class="elem_width noIcon">
                <workers-select label="Линейный руководитель" v-model="user.head"/>
              </v-flex>
              <v-spacer class="spacer_width"/>
            </v-layout>
          </v-form>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
  import {userQuery, modifyUser, changeUserPassword, fireUser, hireUser, setSuperUser, saveUserAvatar} from './query'
  import Alarms from '../Alarms.vue'
  import UserHeader from './Header.vue'
  import DatePicker from '../DatePicker.vue'
  import UserPasswordDialog from './PasswordDialog.vue'
  import Positions from '../positions/Positions.vue'
  import IntegerField from '../IntegerField'
  import WorkersSelect from '../WorkersSelect'
  import AvatarUpload from '../AvatarUpload'
  import FileUpload from '../FileUpload'

  export default {
    name: 'User',
    components: {
      FileUpload,
      WorkersSelect,
      AvatarUpload,
      IntegerField,
      UserPasswordDialog,
      DatePicker,
      Alarms,
      Positions,
      UserHeader
    },
    metaInfo () {
      return {title: this.user.id ? `Сотрудник - ${this.user.shortName}` : 'Сотрудник'}
    },
    apollo: {
      userQuery: {
        fetchPolicy: 'cache-and-network',
        query: userQuery,
        variables () {
          return {
            userId: this.$route.params.id
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.user = Object.assign({}, data.user)
          return null
        }
      }
    },
    data () {
      return {
        user: {
          id: '',
          lastName: '',
          firstName: '',
          patronym: '',
          fullName: '',
          shortName: '',
          email: '',
          login: '',
          workPhone: '',
          personalPhone: '',
          gender: 'MALE',
          birthDate: '',
          hireDate: null,
          fireDate: null,
          healthy: false,
          isSuperuser: false,
          fired: false,
          head: null,
          avatar: null
        },
        loadingQueriesCount: 0,
        genderItems: [
          {text: 'Мужской', value: 'MALE'},
          {text: 'Женский', value: 'FEMALE'}
        ],
        allowedBirthDates: function (date) {
          date = new Date(date)
          const then = new Date()
          then.setFullYear(then.getFullYear() - 18)
          return date < then
        },
        nonEmptyField: [
          (text) => !!text || 'Поле не может быть пустым'
        ],
        gtZero: [
          (num) => num >= 0 || 'Число должно быть положительным'
        ],
        valid: false,
        saveUserAvatar: saveUserAvatar
      }
    },
    computed: {
      firedTag () {
        return this.user.gender === 'FEMALE' ? 'уволена' : 'уволен'
      },
      age () {
        if (this.user.birthDate) {
          // https://stackoverflow.com/questions/4060004/calculate-age-given-the-birth-date-in-the-format-yyyymmdd
          const today = new Date()
          const birthDate = new Date(this.user.birthDate)
          let age = today.getFullYear() - birthDate.getFullYear()
          const m = today.getMonth() - birthDate.getMonth()
          if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--
          }
          const yearWord = (age) => {
            if (age > 10 && age < 20) {
              return 'лет'
            }
            age %= 10
            if (age === 1) {
              return 'год'
            }
            if (age >= 2 && age <= 4) {
              return 'года'
            }
            return 'лет'
          }
          return age + ' ' + yearWord(age)
        }
      },
      shortUser () {
        return {
          id: this.$route.params.id,
          shortName: this.user.shortName
        }
      }
    },
    methods: {
      saveUser () {
        const userToSend = Object.assign({}, this.user)
        delete userToSend.fired
        delete userToSend.isSuperuser
        delete userToSend.fullName
        delete userToSend.shortName
        delete userToSend.avatar
        delete userToSend.__typename
        this.$apollo.mutate({
          mutation: modifyUser,
          variables: {
            input: userToSend
          }
        }).then(({data}) => {
          if (data.modifyUser.user) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Данные сохранены'
            })
            this.user = Object.assign({}, data.modifyUser.user)
          }
        })
      },
      fireUser (fireDate) {
        this.$apollo.mutate({
          mutation: fireUser,
          variables: {
            input: {
              userId: this.user.id,
              fireDate: fireDate
            }
          }
        }).then(({data}) => {
          if (data.fireUser.success) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: this.user.shortName + ' успешно ' + this.firedTag
            })
            this.$apollo.queries.userQuery.refetch()
          }
        })
      },
      hireUser () {
        this.$apollo.mutate({
          mutation: hireUser,
          variables: {
            input: {
              userId: this.user.id
            }
          }
        }).then(({data}) => {
          if (data.hireUser.success) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: this.user.shortName + ' успешно принят' +
              (this.user.gender === 'FEMALE' ? 'a' : '') + ' обратно'
            })
            this.$apollo.queries.userQuery.refetch()
          }
        })
      },
      changePassword (newPassword) {
        this.$apollo.mutate({
          mutation: changeUserPassword,
          variables: {
            input: {
              userId: this.user.id,
              password: newPassword
            }
          }
        }).then(({data}) => {
          if (data.changeUserPassword.success) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Пароль успешно сменён'
            })
          }
        })
      },
      setSuperUser (value) {
        this.$apollo.mutate({
          mutation: setSuperUser,
          variables: {
            input: {
              userId: this.user.id,
              isSuperuser: this.user.isSuperuser
            }
          }
        }).then(({data}) => {
          if (data.setSuperUser.success) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Статус суперпользователя ' + (this.user.isSuperUser ? 'добавлен' : 'отозван')
            })
          } else {
            this.user.isSuperuser = !this.user.isSuperuser
          }
        }).catch(() => {
          this.user.isSuperuser = !value
        })
      }
    }
  }
</script>

<style>
  .elem_width {
    width: 22%;
    min-width: 140px;
  }

  .spacer_width {
    width: 10%;
    min-width: 0;
  }

  .noIcon {
    padding-left: 40px;
  }
</style>
