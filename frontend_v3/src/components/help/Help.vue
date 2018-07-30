<template>
  <v-card>
    <v-card-title>
      <span class="ma-0 headline">Справочный раздел</span>
    </v-card-title>
    <v-card-text class="px-5 help" v-html="markdownHtml" />
  </v-card>
</template>

<script>
  import gql from 'graphql-tag'
  import showdown from 'showdown'

  export default {
    name: 'help',
    metaInfo: {
      title: 'Справочный раздел'
    },
    apollo: {
      mdContent: {
        query: gql`{ mdContent: helpMdText }`
      }
    },
    data () {
      return {
        mdContent: ''
      }
    },
    computed: {
      markdownHtml () {
        const converter = new showdown.Converter({tables: true})
        return converter.makeHtml(this.mdContent)
      }
    }
  }
</script>

<style>
  .help table {
    border-collapse: collapse;
    margin-bottom: 10px;
  }

  .help h2, .help h3 {
    margin: 10px 0;
  }

  .help ul {
    margin-left: 16px;
    margin-bottom: 10px;
  }

  .help th {
    background-color: #9ccc65;
    border: solid 1px #8d8d8d;
    padding: 3px 6px;
  }

  .help td {
    border: solid 1px #8d8d8d;
    padding: 3px 6px;
  }
</style>
