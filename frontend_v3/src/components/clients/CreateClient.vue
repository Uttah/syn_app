<template>
  <div>
    <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition"
              persistent scrollable :overlay=false>
      <v-card>
        <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
          <v-btn icon @click.native="closeDialog" dark>
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Добавление контрагента</v-toolbar-title>
          <v-spacer/>
          <v-toolbar-items>
            <v-btn flat @click="createClient" :disabled="!valid" :loading="loading">Создать</v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <v-form v-model="valid" xs12>
            <v-container>
              <v-layout v-if="client.kind==1" wrap justify-space-between>
                <v-flex xs5>
                  <client-name-picker v-model="client.name"/>
                </v-flex>
                <v-flex xs5>
                  <v-text-field label="Полное наименование" v-model="client.fullName"/>
                </v-flex>
              </v-layout>
              <v-layout v-else="client.kind==2" wrap justify-space-between>
                <v-flex xs5>
                  <v-text-field label="Имя" :rules="nonEmptyField" v-model="client.name"/>
                </v-flex>
                <v-flex xs5>
                  <v-text-field label="Полное имя" v-model="client.fullName"/>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs3>
                  <v-text-field label="Номер телефона" mask="8 (###) ###-##-##" v-model="client.phoneNumber"/>
                </v-flex>
                <v-spacer/>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs5>
                  <client-kind-select label="Тип контрагента" v-model="client.kind"/>
                </v-flex>
                <v-flex xs5>
                  <client-relation-select label="Взаимоотношения" v-model="client.relation"/>
                </v-flex>
              </v-layout>

              <v-layout v-if="client.kind==1" wrap justify-space-between>
                <v-flex xs3 class="pr-3">
                  <v-text-field label="ИНН" mask="############" counter="12" v-model="client.INN"/>
                </v-flex>
                <v-flex xs3 class="px-3">
                  <v-text-field label="КПП" mask="#########" counter="9" v-model="client.KPP"/>
                </v-flex>
                <v-flex xs3 class="px-3">
                  <v-text-field label="ОКПО" mask="########" counter="8" v-model="client.OKPO"/>
                </v-flex>
                <v-flex xs3 class="pl-3">
                  <v-text-field label="ОГРН" mask="#############" counter="13" v-model="client.OGRN"/>
                </v-flex>
              </v-layout>

              <v-layout v-if="client.kind==2" wrap justify-space-between>
                <v-flex xs4 class="pr-3">
                  <v-text-field label="ИНН" mask="############" counter="12" v-model="client.INN"/>
                </v-flex>
                <v-flex xs4 class="px-3">
                  <v-text-field label="ОКПО" mask="########" counter="8" v-model="client.OKPO"/>
                </v-flex>
                <v-flex xs4 class="pl-3">
                  <v-text-field label="ОГРН" mask="#############" counter="13" v-model="client.OGRN"/>
                </v-flex>
              </v-layout>

              <v-layout wrap>
                <v-flex xs12>
                  <v-text-field label="Юр. адрес" v-model="client.legalAddress"/>
                </v-flex>
              </v-layout>
              <v-layout wrap>
                <v-flex xs12>
                  <v-text-field label="Фактический адрес" v-model="client.streetAddress"/>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs12>
                  <v-text-field label="Другое" v-model="client.other" multi-line/>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs4>
                  <workers-select label="Менеджер" v-model="client.manager"/>
                </v-flex>
                <v-spacer/>
              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import auth from '../../auth/auth'
  import ClientKindSelect from '../ClientKindSelect'
  import ClientRelationSelect from '../ClientRelationSelect'
  import ClientNamePicker from '../ClientNamePicker'
  import WorkersSelect from '../WorkersSelect'
  import {createClient, allClients} from './query'

  export default {
    name: 'CreateClient',
    components: {
      ClientKindSelect,
      ClientRelationSelect,
      ClientNamePicker,
      WorkersSelect
    },
    data () {
      return {
        auth: auth,
        dialog: false,
        dialogDelete: false,
        loading: false,
        valid: false,
        client: {
          name: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      openDialog () {
        this.dialog = true
        this.client.manager = auth.user.id
      },
      closeDialog () {
        this.dialog = false
      },
      createClient () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createClient,
            variables: {
              input: {
                name: this.client.name,
                kindId: this.client.kind,
                relationId: this.client.relation,
                fullName: this.client.fullName,
                INN: this.client.INN,
                KPP: this.client.KPP,
                OKPO: this.client.OKPO,
                OGRN: this.client.OGRN,
                legalAddress: this.client.legalAddress,
                streetAddress: this.client.streetAddress,
                phoneNumber: this.client.phoneNumber,
                managerId: this.client.manager,
                other: this.client.other
              }
            },
            update: (store, {data: {addClient}}) => {
              const query = {query: allClients}
              try {
                const data = store.readQuery(query)
                data.allClients.push(addClient.client)
                query.data = data
                store.writeQuery(query)
              } catch (e) {
              }
            }
          }
        ).then(({data}) => {
          this.loading = false
          this.$emit('success')
          this.closeDialog()
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>

