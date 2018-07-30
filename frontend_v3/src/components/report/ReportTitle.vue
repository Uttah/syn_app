<template>
    <span class="ma-0 headline">Отчет о работе
      <span class="grey--text text--darken-2">{{ getCheckedString }}</span>
    </span>
</template>

<script>
  import utils from '../utils'

  export default {
    name: 'report-title',
    props: ['getReport'],
    mixins: [utils],
    computed: {
      getCheckedString () {
        if (this.getReport.userAdded && this.getReport.timeEdited) {
          if (this.getReport.deleted) {
            return '(удалён ГИПом)'
          }
          let result = '('
          if (this.getReport.checkedBy && this.getReport.userAdded.id === this.getReport.checkedBy.id) {
            result += 'внесен/проверен ' + this.formatDateTime(this.getReport.timeEdited) + ' ' +
              this.getReport.userAdded.shortName
          } else {
            result += 'внесён ' + this.formatDateTime(this.getReport.timeEdited) + ' ' +
              this.getReport.userAdded.shortName
            if (this.getReport.checkedBy) {
              result += ', проверен ' + this.formatDateTime(this.getReport.timeChecked) + ' ' +
                this.getReport.checkedBy.shortName
            }
          }
          result += ')'
          return result
        } else {
          return ''
        }
      }
    }
  }
</script>
