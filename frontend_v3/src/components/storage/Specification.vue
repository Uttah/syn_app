<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Спецификации</span>
        <v-spacer/>
        <v-text-field label="Поиск" v-model="searchQuery"/>
        <v-btn color="primary" @click="createSpecification">Создать спецификацию</v-btn>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="allSpecification.specifications"
        :total-items="allSpecification.totalCount"
        :pagination.sync="pagination"
        :rows-per-page-items="rpp"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        rows-per-page-text="Строк на странице"
        no-data-text="Нет доступных данных"
        must-sort
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr @click="editSpecification(props.item)">
            <td>{{ formatProject(props.item.project.number) }}</td>
            <td>{{ props.item.pressmark }}</td>
            <td style="max-width: 400px">{{ props.item.objectName }}</td>
            <td>{{ props.item.sectionName }}</td>
            <td>{{ props.item.organization }}</td>
            <td>{{ props.item.documentName }}</td>
            <td>{{ props.item.state }}</td>
          </tr>
        </template>
        <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
          С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
        </template>
      </v-data-table>
      <c-r-u-d-specification ref="crud" @success="success" @reopen="reopen"/>
    </v-card-text>
  </v-card>
</template>

<script>
  import _ from 'lodash'
  import {pagedSpecification} from './query'
  import CRUDSpecification from './CRUDSpecification'
  import utilsMixin from '../utils'

  export default {
    name: 'Specification',
    metaInfo: {
      title: 'Спецификации'
    },
    components: {
      CRUDSpecification
    },
    mixins: [
      utilsMixin
    ],
    data () {
      return {
        searchQuery: '',
        search: '',
        allSpecification: [],
        loadingQueriesCount: 0,
        rpp: [
          25, 50, 100
        ],
        headers: [
          {text: 'Проект', value: 'project'},
          {text: 'Шифр', value: 'pressmark'},
          {text: 'Название объекта', value: 'objectName'},
          {text: 'Название раздела', value: 'sectionName'},
          {text: 'Организация', value: 'organization'},
          {text: 'Название документа', value: 'documentName'},
          {text: 'Стадия', value: 'state'}
        ],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalCount: 0,
          sortBy: 'project'
        })
      }
    },
    apollo: {
      query: {
        query: pagedSpecification,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            paged: {
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              first: this.pagination.rowsPerPage,
              sortBy: this.pagination.sortBy,
              desc: this.pagination.descending,
              search: this.search
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.allSpecification = data.pagedSpecification
        }
      }
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.search = this.searchQuery
      }, 500),
      createSpecification () {
        this.$refs.crud.openDialog()
      },
      editSpecification (val) {
        window.open('specification/' + val.id).focus()
        // Не работает
        // this.$router.push({
        //   name: 'specification',
        //   params: {id: val.id}
        // })
      },
      success () {
        this.$apollo.queries.query.refetch()
      },
      reopen (val) {
        setTimeout(() => {
          this.editSpecification(val)
        }, 500)
      }
    },
    watch: {
      searchQuery: function () {
        this.searchOperation()
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      }
    }
  }
</script>

