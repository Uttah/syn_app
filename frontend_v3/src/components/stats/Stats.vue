<template>
  <div>
    <div class="pt-3 pr-5 pl-5">
      <months-filter v-model="date" hide-details/>
    </div>
    <v-tabs fixed centered color="background">
      <v-tab href="#tab-hours">Часы</v-tab>
      <v-tab href="#tab-projects">Проекты</v-tab>
      <v-tab-item key="1" id="tab-hours">
        <div id="chartHours" style="width: 100%; height: 400px;"></div>
        <span class="title ml-3">Всего: {{ monthHours }} ч. <span v-if="monthMinutes !== 0">{{monthMinutes}} м.</span></span>
      </v-tab-item>
      <v-tab-item key="2" id="tab-projects">
        <div id="chartProjects" style="width: 100%; height: 400px;"></div>
      </v-tab-item>
    </v-tabs>
  </div>
</template>

<script>
  import {hoursProjectsStats} from './query'
  import MonthsFilter from '../MonthsFilter'
  import utilMixin from '../utils'
  import AmCharts from 'amcharts3' //  eslint-disable-line no-unused-vars
  import AmSerial from 'amcharts3/amcharts/serial' //  eslint-disable-line no-unused-vars
  import AmPie from 'amcharts3/amcharts/pie' //  eslint-disable-line no-unused-vars

  export default {
    components: {MonthsFilter},
    name: 'stats',
    metaInfo: {
      title: 'Статистика'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: hoursProjectsStats,
        variables () {
          return {
            date: this.date
          }
        },
        update (data) {
          if (data.hours.reports.length > 0) {
            let hoursData = JSON.parse(JSON.stringify(data.hours.reports))
            hoursData.map(item => {
              item.reportDate = this.formatDate(item.reportDate)
              let projects = item.projects.split(', ')
              for (let i = 0; i < projects.length; i++) {
                projects[i] = this.pad(projects[i], 5)
              }
              item.projects = projects.join(', ')
              if (item.sum < 7.5 && !item.dayOff) {
                let result = this.getHoursMinutes(item.sum)
                item.shortHours = result.hours
                item.shortMinutes = result.minutes
                item.shortColor = '#FFEE58'
                item.shortValue = Math.max(1, item.sum)
              }
              if (item.sum >= 7.5 && item.sum <= 8 && !item.dayOff) {
                let result = this.getHoursMinutes(item.sum)
                item.normalValue = item.sum
                item.normalHours = result.hours
                item.normalMinutes = result.minutes
                item.normalHoursText = item.normalHours
                item.normalMinutesText = item.normalMinutes
                item.normalColor = '#66BB6A'
              }
              if (item.sum > 8 && !item.dayOff) {
                item.normalValue = 8.0
                item.normalHours = 8
                item.normalMinutes = 0
                let result = this.getHoursMinutes(item.sum)
                item.normalHoursText = result.hours
                item.normalMinutesText = result.minutes
                item.normalColor = '#66BB6A'
                item.sum = item.sum - 8
                result = this.getHoursMinutes(item.sum)
                item.muchHours = result.hours
                item.muchMinutes = result.minutes
                item.muchValue = Math.max(1, item.sum)
                item.muchColor = '#ef5350'
              }
              if (item.dayOff) {
                let result = this.getHoursMinutes(item.sum)
                item.weekendHours = result.hours
                item.weekendMinutes = result.minutes
                item.weekendColor = '#42A5F5'
                item.weekendValue = Math.max(1, item.sum)
              }
              return item
            })
            let result = this.getHoursMinutes(data.hours.monthSum)
            this.monthHours = result.hours
            this.monthMinutes = result.minutes

            let workingDays = JSON.parse(JSON.stringify(data.workingDays))

            workingDays.forEach(item => {
              item.reportDate = this.formatDate(item.date)
              delete item.date
              let alreadyIn = hoursData.some(item2 => {
                return item.reportDate === item2.reportDate
              })
              if (!alreadyIn) {
                hoursData.push(item)
              }
            })

            hoursData.sort((d1, d2) => {
              d1 = d1.reportDate.split('.')
              d2 = d2.reportDate.split('.')
              let date1 = new Date(d1[2], d1[1], d1[0])
              let date2 = new Date(d2[2], d2[1], d2[0])
              return date1 - date2
            })

            this.chartHours.dataProvider = hoursData
            if (hoursData.length > 18) {
              this.chartHours.fontSize = 8
            } else {
              this.chartHours.fontSize = 11
            }
            this.chartHours.validateData()
          } else {
            this.chartHours.dataProvider = []
            this.monthHours = 0
            this.monthMinutes = 0
            this.chartHours.validateData()
          }
          if (data.projectsStats.length > 0) {
            let projectsStats = JSON.parse(JSON.stringify(data.projectsStats))
            projectsStats.map(item => {
              item.project = this.pad(item.project, 5)
              let result = this.getHoursMinutes(item.sum)
              item.hours = result.hours
              item.minutes = result.minutes
              return item
            })
            this.chartProjects.dataProvider = projectsStats
            if (projectsStats.length > 8) {
              this.chartProjects.labelText = ''
            } else {
              this.chartProjects.labelText = ' '
            }
            this.chartProjects.validateData()
          } else {
            this.chartProjects.dataProvider = []
            this.chartProjects.validateData()
          }
        }
      }
    },
    mounted () {
      this.chartHours = window.AmCharts.makeChart('chartHours', //  eslint-disable-line no-unused-vars
        {
          'type': 'serial',
          'theme': 'light',
          'dataProvider': [],
          'valueAxes': [{
            'stackType': 'regular',
            'axisAlpha': 0.3,
            'gridAlpha': 0,
            'dashLength': 0,
            'maximum': 20,
            'minimum': 0,
            'autoGridCount': false,
            'gridCount': 24
          }],
          'startDuration': 1,
          'balloon': {
            'fontSize': '11'
          },
          'graphs': [
            {
              'balloonText': ' ',
              'labelText': ' ',
              'fontSize': '11',
              'fillColorsField': 'shortColor',
              'fillAlphas': 0.8,
              'lineAlpha': 0.2,
              'type': 'column',
              'valueField': 'shortValue',
              'labelFunction': function (item) {
                if (item.dataContext.shortMinutes !== 0) {
                  return item.dataContext.shortHours + ' ч. ' + item.dataContext.shortMinutes + ' м.'
                }
                return item.dataContext.shortHours + ' ч.'
              },
              'balloonFunction': function (item) {
                if (item.dataContext.shortMinutes !== 0) {
                  return item.dataContext.reportDate + ': <b>' + item.dataContext.shortHours + ' ч. ' +
                    item.dataContext.shortMinutes + ' м.</b><br>Проекты: ' + item.dataContext.projects
                }
                return item.dataContext.reportDate + ': <b>' + item.dataContext.shortHours + ' ч. ' +
                  '</b><br>Проекты: ' + item.dataContext.projects
              }
            },
            {
              'balloonText': ' ',
              'labelText': ' ',
              'fontSize': '11',
              'fillColorsField': 'normalColor',
              'fillAlphas': 0.8,
              'lineAlpha': 0.2,
              'type': 'column',
              'valueField': 'normalValue',
              'labelFunction': function (item) {
                if (item.dataContext.normalMinutes !== 0) {
                  return item.dataContext.normalHours + ' ч. ' + item.dataContext.normalMinutes + ' м.'
                }
                return item.dataContext.normalHours + ' ч.'
              },
              'balloonFunction': function (item) {
                if (item.dataContext.normalMinutes !== 0 || item.dataContext.muchMinutes) {
                  return item.dataContext.reportDate + ': <b>' + item.dataContext.normalHoursText + ' ч. ' +
                    item.dataContext.normalMinutesText + ' м.</b><br>Проекты: ' + item.dataContext.projects
                }
                return item.dataContext.reportDate + ': <b>' + item.dataContext.normalHoursText + ' ч. ' +
                  '</b><br>Проекты: ' + item.dataContext.projects
              }
            },
            {
              'balloonText': '',
              'labelText': ' ',
              'fontSize': '11',
              'fillColorsField': 'muchColor',
              'fillAlphas': 0.8,
              'lineAlpha': 0.2,
              'type': 'column',
              'valueField': 'muchValue',
              'labelFunction': function (item) {
                if (item.dataContext.muchHours !== 0 && item.dataContext.muchMinutes === 0) {
                  return item.dataContext.muchHours + ' ч.'
                }
                return item.dataContext.muchHours + ' ч. ' + item.dataContext.muchMinutes + ' м.'
              }
            },
            {
              'balloonText': ' ',
              'labelText': ' ',
              'fontSize': '11',
              'fillColorsField': 'weekendColor',
              'fillAlphas': 0.8,
              'lineAlpha': 0.2,
              'type': 'column',
              'valueField': 'weekendValue',
              'labelFunction': function (item) {
                if (item.dataContext.weekendMinutes !== 0) {
                  return item.dataContext.weekendHours + ' ч. ' + item.dataContext.weekendMinutes + ' м.'
                }
                return item.dataContext.weekendHours + ' ч.'
              },
              'balloonFunction': function (item) {
                if (item.dataContext.weekendMinutes !== 0) {
                  return item.dataContext.reportDate + ': <b>' + item.dataContext.weekendHours + ' ч. ' +
                    item.dataContext.weekendMinutes + ' м.</b><br>Проекты: ' + item.dataContext.projects
                }
                return item.dataContext.reportDate + ': <b>' + item.dataContext.weekendHours + ' ч. ' +
                  '</b><br>Проекты: ' + item.dataContext.projects
              }
            }
          ],
          'chartCursor': {
            'categoryBalloonEnabled': false,
            'cursorAlpha': 0,
            'zoomable': false
          },
          'categoryField': 'reportDate',
          'categorySizeField': '20',
          'fontSize': 11,
          'categoryAxis': {
            'gridPosition': 'start',
            'gridAlpha': 0,
            'tickPosition': 'start',
            'tickLength': 20
          },
          'export': {
            'enabled': true
          }
        }
      )
      this.chartProjects = window.AmCharts.makeChart('chartProjects', //  eslint-disable-line no-unused-vars
        {
          'type': 'pie',
          'theme': 'light',
          'legend': {
            'position': 'right',
            'valueText': '[[hours]] ч. [[minutes]] м. - [[percents]] %',
            'marginRight': 100,
            'autoMargins': false,
            'valueWidth': 140,
            'valueFunction': function (item) {
              if (item.dataContext.minutes !== 0) {
                return item.dataContext.hours + ' ч. ' + item.dataContext.minutes + ' м. - ' +
                  item.percents.toFixed(2) + '%'
              }
              return item.dataContext.hours + ' ч. - ' + item.percents.toFixed(2) + '%'
            }
          },
          'dataProvider': [],
          'valueField': 'sum',
          'titleField': 'project',
          'labelText': ' ',
          'balloonText': ' ',
          'balloon': {
            'fixedPosition': true
          },
          'labelFunction': function (item) {
            if (item.dataContext.minutes !== 0) {
              return 'Проект ' + item.dataContext.project + ': ' + item.percents.toFixed(2) +
                '% (' + item.dataContext.hours + ' ч. ' + item.dataContext.minutes + ' м.)'
            }
            return 'Проект ' + item.dataContext.project + ': ' + item.percents.toFixed(2) +
              '% (' + item.dataContext.hours + ' ч.)'
          },
          'balloonFunction': function (item) {
            if (item.dataContext.minutes !== 0) {
              return 'Проект ' + item.dataContext.project + ': ' + item.percents.toFixed(2) +
                '% (' + item.dataContext.hours + ' ч. ' + item.dataContext.minutes + ' м.)'
            }
            return 'Проект ' + item.dataContext.project + ': ' + item.percents.toFixed(2) +
              '% (' + item.dataContext.hours + ' ч.)'
          },
          'export': {
            'enabled': true
          }
        }
      )
    },
    data () {
      return {
        chartHours: null,
        chartProjects: null,
        date: this.getDefaultFilterDate(),
        monthHours: 0,
        monthMinutes: 0
      }
    },
    methods: {
      getHoursMinutes (time) {
        let hours, minutes
        hours = time - (time % 1)
        if (time % 1 !== 0) {
          minutes = Math.round((time % 1) * 60)
        } else {
          minutes = 0
        }
        return {hours, minutes}
      }
    }
  }
</script>
