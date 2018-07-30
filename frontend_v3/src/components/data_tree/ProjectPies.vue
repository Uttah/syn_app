<template>
  <div>
    <div v-if="type==='hours'">
      <div id="chartProjectHoursPie" style="width: 100%; height: 400px;"></div>
      <span class="title pl-3">{{ projectAnalysisPieData.name }}: {{ projectAnalysisPieData.hours.toFixed(2)}} ч.</span>
    </div>
    <div v-if="type==='money'">
      <div id="chartProjectMoneyPie" style="width: 100%; height: 400px;"></div>
      <span class="title pl-3">{{ projectAnalysisPieData.name }}: {{ projectAnalysisPieData.money.toLocaleString()}} руб.</span>
    </div>
  </div>
</template>

<script>
  import utilMixin from '../utils'
  import AmCharts from 'amcharts3' //  eslint-disable-line no-unused-vars
  import AmPie from 'amcharts3/amcharts/pie' //  eslint-disable-line no-unused-vars

  export default {
    name: 'project-pies',
    metaInfo: {
      title: 'Статистика по проектам'
    },
    mixins: [utilMixin],
    mounted () {
      this.chartProjectHoursPie = window.AmCharts.makeChart('chartProjectHoursPie', //  eslint-disable-line no-unused-vars
        {
          'type': 'pie',
          'theme': 'light',
          'dataProvider': this.projectAnalysisPieData.children,
          'valueField': 'hours',
          'titleField': 'name',
          'labelText': '',
          'balloonText': '[[name]]: [[hours]] ч. - [[percents]] %',
          'balloon': {
            'fixedPosition': true
          },
          startEffect: 'easeInSine',
          startDuration: 0.5,
          'balloonFunction': function (item) {
            return item.dataContext.name + ': ' + item.dataContext.hours.toFixed(2) + ' ч. - ' + item.percents.toFixed(2) + ' %'
          },
          'export': {
            'enabled': true
          }
        }
      )
      this.chartProjectMoneyPie = window.AmCharts.makeChart('chartProjectMoneyPie', //  eslint-disable-line no-unused-vars
        {
          'type': 'pie',
          'theme': 'light',
          'dataProvider': this.projectAnalysisPieData.children,
          'valueField': 'money',
          'titleField': 'name',
          'labelText': '',
          'balloonText': '[[name]]: [[money]] руб. - [[percents]] %',
          'balloon': {
            'fixedPosition': true
          },
          startEffect: 'easeInSine',
          startDuration: 0.5,
          'balloonFunction': function (item) {
            return item.dataContext.name + ': ' + item.dataContext.money.toLocaleString() + ' руб. - ' + item.percents.toFixed(2) + ' %'
          },
          'export': {
            'enabled': true
          }
        }
      )
    },
    data () {
      return {
        chartProjectHoursPie: null,
        chartProjectMoneyPie: null,
        projectAnalysisPieData: JSON.parse(localStorage.getItem('data-tree-node$ProjectAnalysisPieData')).data,
        type: this.$route.params.type
      }
    }
  }
</script>
