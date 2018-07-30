<template>
  <div>
    <v-dialog v-model="dialogConfirmDelete" persistent max-width="700px">
      <v-card>
        <v-card-title>
          <span class="subheading">
            Вы действительно хотите удалить товар "{{ itemGoodText.goodKindText }}"
            <span v-if="itemGood.defect">некондиция</span>
            со склада "{{ itemGoodText.warehouseText }}"
            в количестве {{ itemGood.count }} {{ itemGoodText.unitText }}?
          </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogConfirmDelete = false">Отмена</v-btn>
          <v-btn v-if="showDeleteButton" flat @click.native="deleteGoodFunc" :disabled="loading"
                 :loading="loading">Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogConfirmUpdate" persistent max-width="700px">
      <v-card>
        <v-card-title>
          <span class="subheading">
            Вы действительно хотите обновить товар "{{ itemGoodText.goodKindText }}"
            <span v-if="itemGood.defect">некондиция</span>
            на складе "{{ itemGoodText.warehouseText }}"
            в количестве {{ itemGood.count }} {{ itemGoodText.unitText }}?
          </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogConfirmUpdate = false">Отмена</v-btn>
          <v-btn v-if="showUpdateButton" flat @click.native="updateGoodFunc" :disabled="!valid || loading"
                 :loading="loading">Обновить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition" persistent scrollable :overlay=false>
      <v-card color="grey lighten-4">
        <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
          <v-btn icon @click.native="closeDialog" dark>
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Обновление/Удаление товара на складе</v-toolbar-title>
          <v-spacer/>
          <v-toolbar-items>
            <v-btn v-if="showDeleteButton" color="blue darken-1" flat @click.native="dialogConfirmDelete = true"
                   :disabled="loading || !canDelete"
                   :loading="loading">Удалить
            </v-btn>
            <v-btn v-if="showUpdateButton" color="blue darken-1" flat @click.native="dialogConfirmUpdate = true"
                   :disabled="!valid || loading || !canUpdate"
                   :loading="loading">Обновить
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <storage-item-dialog v-model="itemGood" @itemGoodText="getItemGoodText"
                               :valid.sync="valid" :disabled="!canUpdate"/>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>


<script>
  import StorageItemDialog from './StorageItemDialog.vue'
  import auth from '../../auth/auth'
  import {updateGood, deleteGood} from './query'

  export default {
    name: 'UpdateStorageDialog',
    props: [
      'value',
      'itemGood'
    ],
    components: {
      StorageItemDialog,
      auth
    },
    data () {
      return {
        dialog: false,
        dialogConfirmUpdate: false,
        dialogConfirmDelete: false,
        valid: false,
        loading: false,
        itemGoodText: {
          goodKindText: null,
          warehouseText: null,
          unitText: null
        },
        canUpdate: auth.hasPermission('warehouse.change_good'),
        canDelete: auth.hasPermission('warehouse.delete_good')
      }
    },
    watch: {
      value: function (val) {
        this.dialog = val
      },
      dialog: function (val) {
        this.$emit('input', val)
      }
    },
    computed: {
      showUpdateButton () {
        return auth.hasPermission('warehouse.change_good')
      },
      showDeleteButton () {
        return auth.hasPermission('warehouse.delete_good')
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
        this.dialogConfirmUpdate = false
        this.dialogConfirmDelete = false
      },
      updateGoodFunc () {
        this.itemGood.projectId = !Array.isArray(this.itemGood.projectId) ? this.itemGood.projectId : null
        this.$apollo.mutate(
          {
            mutation: updateGood,
            variables: {
              input: this.itemGood
            }
          }
        ).then(({data}) => {
          if (data.updateGood.good.id) {
            this.closeDialog()
            this.$emit('updated')
          }
        })
      },
      deleteGoodFunc () {
        this.$apollo.mutate(
          {
            mutation: deleteGood,
            variables: {
              input: {
                id: this.itemGood.id
              }
            }
          }
        ).then(({data}) => {
          if (data.deleteGood.result) {
            this.closeDialog()
            this.$emit('deleted')
          }
        })
      },
      getItemGoodText (item) {
        this.itemGoodText = item
      }
    }
  }
</script>
