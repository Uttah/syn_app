<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-btn color="fired" slot="activator">Уволить</v-btn>
    <v-card>
      <v-card-title>
        <span class="subheading">
          Вы действительно хотите снять сотрудника
          <span class="d-inline-block">{{ shortName }}</span>
          со всех занимаемых должностей и уволить?
        </span>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs10 offset-xs1>
              <date-picker v-model="date" label="Дата увольнения"/>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <span class="subheading ml-3 error--text" v-if="!date">Необходимо указать дату</span>
        <v-spacer/>
        <v-btn color="blue darken-1" flat @click.native="dialog = false">Закрыть</v-btn>
        <v-btn color="blue darken-1" flat :disabled="!date" @click.native="fireUser">Уволить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import DatePicker from '../DatePicker.vue'

  export default {
    name: 'UserFireDialog',
    props: ['shortName', 'value'],
    components: {
      DatePicker
    },
    data () {
      return {
        dialog: false,
        date: this.value
      }
    },
    watch: {
      value: function (val) {
        this.date = val
      },
      date: function (val) {
        this.$emit('input', val)
      }
    },
    methods: {
      fireUser () {
        this.dialog = false
        this.$emit('fire')
      }
    }
  }
</script>
