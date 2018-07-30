<template>
  <div>
    <v-menu v-if="!hideRowActivator" lazy v-model="dialog" transition="scale-transition" offset-y full-width :disabled="disabled || readonly">
      <v-text-field slot="activator" :label="label" v-model="getNameString" :required="required" :disabled="disabled"
                    :hide-details="hideDetails" readonly @focus="$emit('focus')"
                    @blur="$emit('blur')" style="width: 480px"/>
      <v-card @click.native.stop width="480px" class="px-2 pt-2 pb-3">
        <v-layout>
          <v-flex xs3 mx-2>
            <v-select label="Форма" :rules="nonEmptyField" :items="organizationForm" v-model="organizationFormData"/>
          </v-flex>
          <v-flex xs9 mx-2>
            <v-text-field label="Наименование" :rules="nonEmptyField" v-model="textData"/>
          </v-flex>
        </v-layout>
      </v-card>
    </v-menu>

    <v-dialog v-if="hideRowActivator" v-model="dialog" persistent scrollable lazy max-width="700px">
      <v-card>
        <v-card-title>
          <span class="title">Новый заказчик</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="valid">
            <v-layout>
              <v-flex xs3 mx-2>
                <v-select label="Форма" :rules="nonEmptyField" :items="organizationForm" v-model="organizationFormData"/>
              </v-flex>
              <v-flex xs9 mx-2>
                <v-text-field label="Наименование" :rules="nonEmptyField" v-model="textData"/>
              </v-flex>
            </v-layout>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDialog" :disabled="loading">Отменить</v-btn>
          <v-btn flat @click="saveDialog" :disabled="!valid || loading" :loading="loading">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ClientNamePicker',
    props: {
      hideRowActivator: Boolean,
      propDialog: Boolean,
      value: '',
      label: {
        type: String,
        default: 'Название'
      },
      hideDetails: Boolean,
      required: Boolean,
      disabled: Boolean,
      readonly: Boolean,
      displayText: String
    },
    apollo: {
      organizationForm: {
        fetchPolicy: 'cache-and-network',
        query: gql`query {
          organizationForms {
            name
          }
        }`,
        update (data) {
          return data.organizationForms.map(obj => obj.name)
        }
      }
    },
    data () {
      return {
        valid: false,
        loading: false,
        dialog: false,
        innerValue: this.value,
        textData: '',
        inStart: true,
        organizationForm: [],
        organizationFormData: '',
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    computed: {
      getNameString () {
        if (this.hideRowActivator) {
          this.innerValue = this.organizationFormData + ' "' + this.textData + '"'
          return this.innerValue
        } else {
          if (this.innerValue && this.inStart) {
            this.inStart = false
            let s3RegExp = new RegExp('^(' + this.organizationForm.join('|') + ')', 'g')
            let s3 = this.innerValue.replace(s3RegExp, '')
            this.organizationFormData = this.innerValue.replace(new RegExp(s3, 'g'), '')
            let textDataRegExp = new RegExp('^(' + this.organizationForm.join('|') + ')\\s+"?|"$', 'g')
            this.textData = this.innerValue.replace(textDataRegExp, '')
          }
          this.innerValue = this.organizationFormData + ' "' + this.textData + '"'
          return this.innerValue
        }
      }
    },
    methods: {
      closeDialog () {
        this.$emit('closeDialog')
      },
      saveDialog () {
        this.loading = true
        this.$apollo.mutate({
          mutation: gql`
          mutation ($input: AddClientInput!) {
            addClient(input: $input) {
              client {
                id
                name
              }
            }
          }`,
          variables: {
            input: {
              name: this.getNameString
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.addClient.client) {
            this.$emit('success', data.addClient.client)
            this.closeDialog()
          }
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      propDialog: {
        handler: function (val) {
          this.dialog = this.propDialog
        }
      },
      value: {
        handler: function (val) {
          this.innerValue = val
        },
        deep: true
      },
      innerValue: {
        handler: function (val) {
          this.$emit('input', val)
        }
      },
      getNameString: function (val) {
        this.$emit('update:displayText', val)
      }
    }
  }
</script>
