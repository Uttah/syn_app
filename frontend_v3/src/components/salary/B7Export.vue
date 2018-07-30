<template>
  <v-card>
    <v-card-text style="justify-content: center">
      <v-progress-circular indeterminate size="64" style="width: 100%" v-show="loading"/>
      <div class="text-xs-center" style="width: 100%">{{ loadingLabel }}</div>
    </v-card-text>
  </v-card>
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'b7-export',
    metaInfo: {
      title: 'Экспорт в Б7'
    },
    apollo: {
      q: {
        fetchPolicy: 'network-only',
        query: gql`{ b7Export }`,
        update (data) {
          this.loading = false
          // Сохраняем блоб
          const a = document.createElement('a')
          document.body.appendChild(a)
          a.style = 'display: none'
          let blob = new Blob([data.b7Export], {type: 'application/octet-stream'})
          let url = window.URL.createObjectURL(blob)
          a.href = url
          let fileName = new Date()
          fileName = 'export-' + fileName.toISOString().substr(0, 10) + '.csv'
          a.download = fileName
          a.click()
          window.URL.revokeObjectURL(url)
          this.$router.go(-1)
        }
      }
    },
    data () {
      return {
        loading: true,
        loadingLabel: 'Подготавливаем данные. Пожалуйста, подождите.'
      }
    }
  }
</script>
