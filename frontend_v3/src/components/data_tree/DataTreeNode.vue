<template>
  <li class="data-tree-node">
    <v-menu
      offset-y
      v-model="menuChart"
      absolute
      v-if="isFolder"
      :position-x="MenuChartX"
      :position-y="MenuChartY"
    ><v-list>
        <v-list-tile @click="openHoursPie">
          <v-list-tile-title>Построить диаграмму по часам</v-list-tile-title>
        </v-list-tile>
        <v-list-tile @click="openMoneyPie">
          <v-list-tile-title>Построить диаграмму по затратам</v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>
    <div class="d-inline-flex">
      <img :src="nodeImg">
      <span @click="toggle" @contextmenu="showMenuChart" class="d-inline-flex" :class="{'data-tree-cursor': isFolder}">
        <v-icon v-if="isFolder" class="mr-1">{{ open ? 'mdi-minus-box-outline' : 'mdi-plus-box-outline' }}</v-icon>
        {{ nodeName }}
      </span>
    </div>
    <v-slide-y-transition>
      <ul v-show="open" v-if="isFolder" class="data-tree-list" :class="{'data-tree-node-down': !lastItem}">
        <data-tree-node ref="childNodes" v-for="(model, index) in model.children" @closeMenus="$emit('closeMenus')"
                        :key="index" :index="index" :model="model" :expand-all="expandAll"/>
      </ul>
    </v-slide-y-transition>
  </li>
</template>

<script>
  import dataTreeNodeSide from './data-tree-ticks-side.svg'
  import dataTreeNodeEnd from './data-tree-ticks-end.svg'
  import utilsMixin from '../utils'

  export default {
    name: 'data-tree-node',
    props: {
      model: Object,
      index: Number,
      expandAll: Boolean
    },
    mixins: [
      utilsMixin
    ],
    data () {
      return {
        open: this.expandAll,
        menuChart: false,
        MenuChartX: 0,
        MenuChartY: 0
      }
    },
    computed: {
      isFolder () {
        return this.model.children && this.model.children.length > 0
      },
      lastItem () {
        return this.index === this.$parent.model.children.length - 1
      },
      nodeImg () {
        return this.lastItem ? dataTreeNodeEnd : dataTreeNodeSide
      },
      nodeName () {
        const hours = Number(this.model.hours).toFixed(2).replace('.', ',')
        const money = this.formatMoney(this.model.money)
        return `${this.model.name} (${hours} ч. / ${money} руб.)`
      }
    },
    methods: {
      toggle () {
        if (this.isFolder) {
          this.open = !this.open
        }
      },
      expand () {
        this.open = true
        if (this.$refs.childNodes) {
          this.$refs.childNodes.forEach(ref => ref.expand())
        }
      },
      collapse () {
        this.open = false
        if (this.$refs.childNodes) {
          this.$refs.childNodes.forEach(ref => ref.collapse())
        }
      },
      showMenuChart (e) {
        e.preventDefault()
        this.$emit('closeMenus')
        this.MenuChartX = e.clientX
        this.MenuChartY = e.clientY
        this.$nextTick(() => {
          this.menuChart = true
        })
      },
      closeMenu () {
        this.menuChart = false
        if (this.$refs.childNodes) {
          this.$refs.childNodes.forEach(ref => ref.closeMenu())
        }
      },
      openHoursPie () {
        this.storeValue('ProjectAnalysisPieData', this.model)
        window.open('/project_pies/hours', String(Math.random()), 'width=700,height=500')
      },
      openMoneyPie () {
        this.storeValue('ProjectAnalysisPieData', this.model)
        window.open('/project_pies/money', String(Math.random()), 'width=700,height=500')
      }
    }
  }
</script>

<style>
  .data-tree-list {
    list-style: none;
    margin: 0;
    padding-left: 26px;
  }

  .data-tree-node img {
    position: relative;
    left: -3px;
    width: 24px;
    height: 24px;
  }

  .data-tree-node {
    margin-top: -4px;
    margin-bottom: -4px;
  }

  .data-tree-node-down {
    background: url("data-tree-ticks.svg") repeat-y;
    background-position-x: -0.65px;
    background-position-y: -2px;
    background-size: 24px;
  }

  .data-tree-node > div, .data-tree-node > div > span {
    align-items: center;
  }

  .data-tree-cursor {
    cursor: pointer;
  }
</style>
