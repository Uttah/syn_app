<template>
  <v-card>
    <v-card-title>
      <span class="ma-0 headline" style="width: 100%">Анализ человеко-часов*</span>
      <span class="mt-2" style="width: 100%">Текущая себестоимость человеко/часа:
        <span v-if="!hasPermissionChangeHourPrimeCost">{{ hourPrimeCost }}</span>
        <v-edit-dialog
          v-if="hasPermissionChangeHourPrimeCost"
          :return-value.sync="openEditHourPrimeCostDialog"
          lazy
        >
          <span style="color: black;">{{ hourPrimeCost }}</span>
          <integer-field
            slot="input"
            label="Введите новое значение"
            v-model="hourPrimeCost"
          />
        </v-edit-dialog>
      </span>
      <v-layout wrap justify-left style="align-items: center">
        <v-flex style="max-width: 150px">
          <v-subheader>Схема фильтров:</v-subheader>
        </v-flex>
        <v-flex xs3>
          <select-filters-row :myFilter.sync="myFilter" :filterSchemas="filterSchemas"
                              :selectedSchemaName.sync="selectedSchemaName"/>
        </v-flex>
        <v-flex>
          <v-btn @click="saveFiltersRow" icon title="Сохранить схему">
            <v-icon>save</v-icon>
          </v-btn>
        </v-flex>
        <v-spacer/>
      </v-layout>
      <save-filters-row @saved="saved" :name="selectedSchemaName" :filtersRow="filtersRow"
                        ref="saveFilters"/>
    </v-card-title>
    <v-container fluid fill-height style="min-height: 90px" class="py-0">
      <v-layout wrap justify-left>
        <template v-for="(item, i) in myFilter">
          <v-card :key="i*2" style="min-width: 300px; max-width: 300px">
            <v-card-title class="pa-0">
              <v-toolbar class="pa-0" flat dense>
                <b style="font-size: 20px">{{item.title}}</b>
                <v-spacer/>
                <div class="mt-4 mr-1">
                  <v-checkbox color="black" v-model="item.considerGroup" title="Использовать группировку"/>
                </div>
                <v-menu bottom offset-y class="mr-0">
                  <v-btn icon flat title="Сортировка" slot="activator">
                    <v-icon dark>sort</v-icon>
                  </v-btn>
                  <v-list>
                    <v-list-tile v-for="(option, i) in sortingOptions" :key="i" @click="changeSort(item, option)">
                      <v-icon v-if="item.sortBy === option.kind">{{ item.desc ? 'arrow_downward' : 'arrow_upward' }}
                      </v-icon>
                      <v-list-tile-title>{{ option.title }}</v-list-tile-title>
                    </v-list-tile>
                  </v-list>
                </v-menu>
                <v-btn icon flat @click="removeFilter(i)" title="Удалить группировку" class="ml-0">
                  <v-icon dark>clear</v-icon>
                </v-btn>
              </v-toolbar>
            </v-card-title>
            <v-card-text class="pa-2 pt-0">
              <v-menu :close-on-content-click="false" content-class="whiteback" max-width="400px" full-width>
                <div slot="activator" class="ellipsis">
                  {{ item.displayText ? item.displayText : 'Применить фильтр...' }}
                </div>
                <worker-select v-model="item.filter" v-if="item.name === 'worker'"
                               multiple hide-details :display-text.sync="item.displayText"/>
                <projects-select v-model="item.filter" v-if="item.name === 'project'"
                                 multiple hide-details :display-text.sync="item.displayText"
                                 :currentGip="!hasPermGlobalAnalysis"/>
                <processes-select v-model="item.filter" v-if="item.name === 'process'"
                                  multiple hide-details :display-text.sync="item.displayText"/>
                <sub-processes-select v-model="item.filter" v-if="item.name === 'subProcess'" show-process-name
                                      multiple hide-details
                                      :display-text.sync="item.displayText"/>
                <func-roles-select v-model="item.filter" v-if="item.name === 'funcRole'"
                                   multiple hide-details :display-text.sync="item.displayText"/>
                <places-select v-model="item.filter" v-if="item.name === 'place'"
                               multiple hide-details :display-text.sync="item.displayText"/>
                <project-state-select v-model="item.filter" v-if="item.name === 'projectState'" multiple
                                      hide-details :display-text.sync="item.displayText"/>
                <two-months-picker v-model="limits" v-if="item.name === 'date'"
                                   hide-details :display-text.sync="item.displayText"/>
              </v-menu>
            </v-card-text>
          </v-card>
          <v-icon large v-if="i < myFilter.length - 1" :key="i*2+1">keyboard_arrow_right</v-icon>
        </template>
        <v-spacer/>
        <span>
        <v-menu bottom offset-y>
          <v-btn large fab dark slot="activator" color="primary" title="Добавить группировку">
            <v-icon dark>add</v-icon>
          </v-btn>
          <v-list>
            <v-list-tile v-for="(item, i) in visibleItems" :key="i" @click="addFilter(item)">
              <v-list-tile-title>{{ item.title }}</v-list-tile-title>
            </v-list-tile>
          </v-list>
        </v-menu>
      </span>
      </v-layout>
    </v-container>
    <v-card-text>
      <v-card>
        <v-card-text>
          <data-tree :model="dataTreeData" :loading="loadingQueriesCount > 0"/>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script>
  import WorkerSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import ProcessesSelect from '../ProcessesSelect'
  import SubProcessesSelect from '../SubProcessesSelect'
  import FuncRolesSelect from '../FuncRolesSelect'
  import PlacesSelect from '../PlacesSelect'
  import DataTree from '../data_tree/DataTree'
  import SaveFiltersRow from './SaveFiltersRow'
  import SelectFiltersRow from './SelectFiltersRow'
  import ProjectStateSelect from '../ProjectStateSelect'
  import TwoMonthsPicker from '../TwoMonthsPicker'
  import {projectAnalysisQuery, filterSchemas, getHourPrimeCost, changeHourPrimeCost} from './query'
  import auth from '../../auth/auth'
  import utilMixin from '../utils'
  import IntegerField from '../IntegerField'

  export default {
    name: 'ProjectAnalysis',
    metaInfo: {
      title: 'Анализ человеко-часов'
    },
    mixins: [utilMixin],
    components: {
      IntegerField,
      WorkerSelect,
      ProjectsSelect,
      ProcessesSelect,
      SubProcessesSelect,
      FuncRolesSelect,
      PlacesSelect,
      DataTree,
      SaveFiltersRow,
      SelectFiltersRow,
      ProjectStateSelect,
      TwoMonthsPicker,
      auth
    },
    apollo: {
      dataTreeData: {
        fetchPolicy: 'cache-and-network',
        query: projectAnalysisQuery,
        variables () {
          return {
            filters: this.myFilter.filter(item => item.considerGroup).map((item) => {
              return {
                name: item.name,
                filter: item.filter,
                sortBy: item.sortBy,
                desc: item.desc
              }
            }),
            limits: this.hasDataFilter ? {
              monthStart: this.limits.monthStart,
              monthEnd: this.limits.monthEnd
            } : {
              monthStart: null,
              monthEnd: null
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      },
      filterSchemas: {
        fetchPolicy: 'cache-and-network',
        query: filterSchemas,
        loadingKey: 'loadingQueriesCount'
      },
      getHourPrimeCostQuery: {
        query: getHourPrimeCost,
        update (data) {
          this.hourPrimeCost = data.getHourPrimeCost
          if (auth.user.id === 5) {
            this.hasPermissionChangeHourPrimeCost = true
          }
        }
      }
    },
    data () {
      return {
        myFilter: this.getValue('filter', []),
        items: [
          {
            id: 1,
            name: 'worker',
            title: 'Исполнитель'
          },
          {
            id: 2,
            name: 'project',
            title: 'Проект'
          },
          {
            id: 3,
            name: 'process',
            title: 'Процесс'
          },
          {
            id: 4,
            name: 'subProcess',
            title: 'Подпроцесс'
          },
          {
            id: 5,
            name: 'funcRole',
            title: 'Функц. роль'
          },
          {
            id: 6,
            name: 'place',
            title: 'Место'
          },
          {
            id: 7,
            name: 'projectState',
            title: 'Этап проекта'
          },
          {
            id: 8,
            name: 'date',
            title: 'Месяц'
          }
        ],
        sortingOptions: [
          {kind: 'name', title: 'По названию'},
          {kind: 'hours', title: 'По часам'},
          {kind: 'money', title: 'По затратам'}
        ],
        filtersRow: '',
        dataTreeData: null,
        selectedSchemaName: '',
        filterSchemas: [],
        loadingQueriesCount: 0,
        hasPermGlobalAnalysis: auth.hasPermission('projects.global_analysis'),
        hourPrimeCost: null,
        changeHourPrimeCost: false, // Запрещает отправку запроса на изменение "hourPrimeCost" при первом вызове "watch".
        hasPermissionChangeHourPrimeCost: false,
        openEditHourPrimeCostDialog: false,
        limits: this.getValue('limits', {
          monthStart: null,
          monthEnd: null
        })
      }
    },
    methods: {
      // Метод добавления фильтра
      addFilter (data) {
        // Добавление в массив фильтров
        this.myFilter.push({
          id: data.id, // Id
          name: data.name,
          title: data.title,
          filter: [], // Id элементов в фильтре(Может быть необязательно)
          sortBy: 'name',
          desc: false,
          displayText: '',
          considerGroup: true
        })
      },
      // Метод удаления фильтра
      removeFilter (position) {
        if (this.myFilter[position].name === 'date') {
          this.limits = {
            monthStart: null,
            monthEnd: null
          }
        }
        this.myFilter.splice(position, 1)
      },
      // Изменение сортировки
      changeSort (item, option) {
        if (item.sortBy !== option.kind) {
          item.sortBy = option.kind
          item.desc = false
        } else {
          item.desc = !item.desc
        }
      },
      // Созранение строки фильтров
      saveFiltersRow () {
        this.filtersRow = JSON.stringify(this.myFilter)
        this.$refs.saveFilters.openDialog()
      },
      saved () {
        this.$apollo.queries.filterSchemas.refetch()
      }
    },
    watch: {
      myFilter: {
        handler: function (val) {
          this.storeValue('filter', val)
        },
        deep: true
      },
      limits: {
        handler: function (val) {
          this.storeValue('limits', val)
        },
        deep: true
      },
      hourPrimeCost: function (val) {
        if (auth.user.id === 5 && this.changeHourPrimeCost) {
          val = (val === null ? 0 : val)
          this.$apollo.mutate({
            mutation: changeHourPrimeCost,
            variables: {
              input: {
                value: val
              }
            }
          }).then(({data}) => {
            if (data.changeHourPrimeCost.result) {
              this.$notify({
                group: 'commonNotification',
                duration: 5000,
                text: 'Cебестоимость человеко/часа изменена'
              })
            }
          })
          this.hourPrimeCost = val
        }
        if (!this.changeHourPrimeCost) {
          this.changeHourPrimeCost = true
        }
      }
    },
    computed: {
      visibleItems () {
        return this.items.filter(item => !this.myFilter.some(filter => filter.id === item.id)).sort((a, b) => a.title.localeCompare(b.title))
      },
      hasDataFilter () {
        const filter = this.myFilter.filter(item => item.name === 'date')
        return filter.length > 0 && filter[0].considerGroup
      }
    }
  }
</script>

<style>
  .whiteback {
    background-color: white;
    padding: 0 15px 15px 15px;
  }
</style>
