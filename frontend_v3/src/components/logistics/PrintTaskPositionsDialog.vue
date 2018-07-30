<template>
  <v-dialog fullscreen hide-overlay scrollable v-model="openDialog" >
    <v-card tile>
      <v-toolbar card color="primary" dense>
        <v-btn icon @click="openDialog = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Позиции списком</v-toolbar-title>
      </v-toolbar>
      <table class="ma-4" width="80%">
          <thead>
            <tr>
              <th class="pa-2">№ п/п</th>
              <th class="pa-2">Артикул</th>
              <th class="pa-2" width="80%">Наименование</th>
              <th class="pa-2">Кол-во</th>
            </tr>
          </thead>
          <template v-for='(position,index) in positions'>
            <tr>
              <td>{{index+1}}</td>
              <td>{{position.goodKind.code}}</td>
              <td class="pa-2" style="text-align: left">{{position.goodKind.name}}</td>
              <td>{{position.count + ' ' + position.unit.shortName}}</td>
            </tr>
          </template>
        </table>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'PrintTaskPositionsDialog',
    props: [
      'value',
      'positions'
    ],
    data () {
      return {
        openDialog: false
      }
    },
    watch: {
      value: function (val) {
        this.openDialog = val
      },
      openDialog: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>

<style scoped>
  table {
    border-collapse: collapse
  }
  tr, th, td {
    border: 1px solid black;
    text-align: center
  }
</style>
