import moment from 'moment'
import Lockr from 'lockr'

const production = process.env.NODE_ENV === 'production'

const utilsMixin = {
  methods: {
    formatMoney (amount) {
      if (!amount) {
        amount = 0
      }
      let result = amount.toLocaleString()
      // Округляем до двух знаков после запятой
      const commaPos = result.indexOf(',')
      if (commaPos === -1) {
        result += ',00'
      } else if (commaPos < result.length - 3) {
        result = result.substr(0, commaPos + 3)
      }
      return result
    },
    formatProject (projectNum) {
      return this.pad(projectNum, 5)
    },
    formatDate (textDate) {
      if (textDate) {
        return moment(textDate).format('L')
      } else {
        return ''
      }
    },
    formatMonth (date) {
      if (date) {
        return moment(date).format('MMMM YYYY')
      } else {
        return ''
      }
    },
    pad (n, width, z) {
      z = z || '0'
      n = n + ''
      return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n
    },
    formatDateTime (textDateTime) {
      if (textDateTime) {
        return moment(textDateTime).format('L LT')
      } else {
        return ''
      }
    },
    storeValue (name, val) {
      const _name = this.$options.name + '$' + name
      Lockr.set(_name, val)
    },
    getValue (name, emptyVal) {
      const _name = this.$options.name + '$' + name
      return Lockr.get(_name, emptyVal)
    },
    removeValue (name) {
      const _name = this.$options.name + '$' + name
      Lockr.rm(_name)
    },
    generateFilterDates (topMonth) {
      const monthArray = {
        '1': 'Январь',
        '2': 'Февраль',
        '3': 'Март',
        '4': 'Апрель',
        '5': 'Май',
        '6': 'Июнь',
        '7': 'Июль',
        '8': 'Август',
        '9': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
      }
      let start = new Date(2016, 11, 2)
      let now = topMonth ? new Date(Number(topMonth.substr(0, 4)), Number(topMonth.substr(4)) - 1, 1) : new Date()
      now = new Date(now.getFullYear(), now.getMonth() + 1, 1)
      let months = []
      /* eslint-disable no-unmodified-loop-condition */
      while (start < now) {
        const text = monthArray[String(start.getMonth() + 1)] + ' ' + start.getFullYear()
        const id = String(start.getMonth() + 1) + String(start.getFullYear() - 2000)
        months.push({'month': text, 'id': id})
        start.setMonth(start.getMonth() + 1)
      }
      months.reverse()
      return months
    },
    // Функция Вывод списка всех месяцев после месяца secondDate
    generateFilterDatesRange (topMonth, secondDate) {
      const monthArray = {
        '1': 'Январь',
        '2': 'Февраль',
        '3': 'Март',
        '4': 'Апрель',
        '5': 'Май',
        '6': 'Июнь',
        '7': 'Июль',
        '8': 'Август',
        '9': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
      }
      let month = secondDate.length === 3 ? secondDate.substr(0, 1) : secondDate.substr(0, 2)
      let year = secondDate.substr(-2, 2)

      let start = secondDate ? new Date(Number('20' + year), Number(month) - 2, 1) : new Date()
      start = new Date(start.getFullYear(), start.getMonth() + 1, 1)
      let now = topMonth ? new Date(Number(topMonth.substr(0, 4)), Number(topMonth.substr(4)) - 1, 1) : new Date()
      now = new Date(now.getFullYear(), now.getMonth() + 1, 1)
      let months = []
      while (start < now) {
        const text = monthArray[String(start.getMonth() + 1)] + ' ' + start.getFullYear()
        const id = String(start.getMonth() + 1) + String(start.getFullYear() - 2000)
        months.push({'month': text, 'id': id})
        start.setMonth(start.getMonth() + 1)
      }
      months.reverse()
      return months
    },
    // Возвращает месяц и год в Текстовом виде(Пример: "Сентябрь 2017"). Индекс указывает на падеж месяца
    getNameOfDate (date, idx) {
      const monthArray = {
        '1': ['Январь', 'Января'],
        '2': ['Февраль', 'Февраля'],
        '3': ['Март', 'Марта'],
        '4': ['Апрель', 'Апреля'],
        '5': ['Май', 'Мая'],
        '6': ['Июнь', 'Июня'],
        '7': ['Июль', 'Июля'],
        '8': ['Август', 'Августа'],
        '9': ['Сентябрь', 'Сентября'],
        '10': ['Октябрь', 'Октября'],
        '11': ['Ноябрь', 'Ноября'],
        '12': ['Декабрь', 'Декабря']
      }
      if (date === null) {
        let now = new Date()
        return monthArray[String(now.getMonth() + 1)][idx] + ' ' + now.getFullYear()
      } else {
        let month = date.length === 3 ? date.substr(0, 1) : date.substr(0, 2)
        let year = date.substr(-2, 2)
        return monthArray[month][idx] + ' ' + '20' + year
      }
    },
    getMnthByDate (date) {
      return String(date.getMonth() + 1) + String(date.getFullYear() - 2000)
    },
    getDateByMnth (mnth) {
      let month = mnth.length === 3 ? mnth.substr(0, 1) : mnth.substr(0, 2)
      let year = '20' + mnth.substr(-2, 2)
      return new Date(Number(year), Number(month - 1), 2)
    },
    // Принимает дату в формате 20183 и возвращает формат 318
    getIdFromMnth (mnth) {
      mnth = String(mnth)
      return mnth.substr(4) + mnth.substr(2, 2)
    },
    getDefaultFilterDate () {
      return this.generateFilterDates()[0].id
    },
    formatTask (report) {
      const formatOriginalText = function (taskText) {
        if (!taskText) {
          taskText = ''
        }
        const regex = /задача\s+№\s*(\d+)/gui
        let newText = taskText
        let m
        while ((m = regex.exec(taskText)) !== null) {
          if (m.index === regex.lastIndex) {
            regex.lastIndex++
          }
          const url = 'https://synergy34.bitrix24.ru/company/personal/user/0/tasks/task/view/' + m[1] + '/'
          const hint = 'Задача № ' + m[1] + ' в Битрикс24'
          const html = '<a href="' + url + '" title="' + hint + '" target="_blank">' + m[0] + '</a>'
          newText = newText.replace(m[0], html)
        }
        return newText.replace(/\n/g, '<br/>')
      }

      if (report.subProcess) {
        const kind = report.subProcess.kind
        if (kind === 'D') {
          const translateRoots = {D: 'служебн', P: 'личн'}
          let text = 'Передвижение на ' + translateRoots[report.car] + 'ом а/м из "' + report.whereFrom + '" '
          text += 'в "' + report.whereTo + '" (' + String(report.distance).replace('.', ',') + ' км)'
          text += ', используя ' + translateRoots[report.gas] + 'ый бензин.'
          return text
        } else if (kind === 'A') {
          let text = 'Серийный номер: SNGY' + this.pad(report.vcProject, 5) + '.' + this.pad(report.vcDigits, 2) +
            '.' + this.pad(report.vcDigitsMinor, 3)
          text += formatOriginalText('\n' + 'Модель: ' + report.model + '\n' + report.task)
          return text
        } else if (kind === 'P') {
          let text = 'Артикул: SNGY' + this.pad(report.vcProject, 5) + '.' + this.pad(report.vcDigits, 2)
          text += formatOriginalText('\n' + 'Модель: ' + report.model + '\n' + report.task)
          return text
        }
      }
      return formatOriginalText(report.task)
    },
    formatURL (url) {
      if (!url) {
        return url
      }
      if (url[0] !== '/') {
        url = '/' + url
      }
      return (production ? '' : '//localhost:8000') + url
    }
  }
}

export default utilsMixin
