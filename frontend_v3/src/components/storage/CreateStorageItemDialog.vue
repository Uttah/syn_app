<template>
  <div>
    <v-dialog v-model="dialogConfirmCreate" persistent max-width="700px">
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите принять на "{{ itemGoodText.warehouseText }}" товар "{{ itemGoodText.goodKindText }}"
          <span v-if="itemGood.defect">некондиция</span> в количестве {{ itemGood.count }} {{ itemGoodText.unitText }}?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogConfirmCreate = false">Отмена</v-btn>
          <v-btn flat @click.native="createItem(true)" :disabled="!valid || loading" :loading="loading">
            Создать и закрыть
          </v-btn>
          <v-btn flat @click.native="createItemContinue" :disabled="!valid || loading" :loading="loading">
            Создать и продолжить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition" persistent scrollable :overlay=false>
      <v-btn full-width color="primary" dark slot="activator" v-if="showCreateButton">Принять товар</v-btn>
      <v-card color="grey lighten-4">
        <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
          <v-btn icon @click.native="closeDialog" dark>
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Принятие товара на склад</v-toolbar-title>
          <v-spacer/>
          <v-toolbar-items>
            <v-btn color="blue darken-1" flat @click.native="dialogConfirmCreate = true" :disabled="!valid || loading"
                   :loading="loading">Создать
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <storage-item-dialog v-model="itemGood" @itemGoodText="getItemGoodText"
                               :valid.sync="valid"/>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>


<script>
  import StorageItemDialog from './StorageItemDialog.vue'
  import {createGood} from './query'
  import auth from '../../auth/auth'

  export default {
    name: 'CreateStorageDialog',
    components: {
      StorageItemDialog,
      auth
    },
    data () {
      return {
        dialog: false,
        dialogConfirmCreate: false,
        valid: false,
        loading: false,
        itemGood: {
          count: null,
          unitId: null,
          note: null,
          goodKindId: null,
          locationId: null,
          defect: false,
          projectId: null,
          responsibleId: null
        },
        itemGoodText: {
          goodKindText: null,
          warehouseText: null,
          unitText: null
        }
      }
    },
    computed: {
      showCreateButton () {
        return auth.hasPermission('warehouse.add_good')
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
        this.$router.push({name: 'storage'})
      },
      createItem (close) {
        close = !!close
        this.loading = true
        this.$apollo.mutate({
          mutation: createGood,
          variables: {
            input: this.itemGood
          }
        }).then(({data}) => {
          this.loading = false
          if (data.createGood.good) {
            if (close) {
              this.closeDialog()
            }
            this.dialogConfirmCreate = false
            this.$emit('created')
          }
        }).catch(() => {
          this.loading = true
        })
      },
      createItemContinue () {
        this.createItem(false)
      },
      getItemGoodText (item) {
        this.itemGoodText = item
      }
    }
  }
</script>
