<template>
  <div class="data-tree-container" :style="{ 'min-height': model && !loading ? '48px' : '100px' }">
    <ul class="data-tree-root" v-if="model">
      <data-tree-node ref="root" :model="model" :expand-all="expandAll" @closeMenus="closeMenus"/>
    </ul>
    <div class="title" v-else :style="{ color: noDataColor }">{{ noDataText }}</div>
    <div class="data-tree-loading" v-show="loading">
      <v-progress-circular indeterminate size="70" color="loading" />
    </div>
    <div class="data-tree-btns" v-if="model">
      <v-btn @click="() => $refs.root.expand()">Развернуть все</v-btn>
      <v-btn @click="() => $refs.root.collapse()">Свернуть все</v-btn>
    </div>
  </div>
</template>

<script>
  import DataTreeNode from './DataTreeNode'

  export default {
    components: {DataTreeNode},
    name: 'data-tree',
    props: {
      model: Object,
      expandAll: Boolean,
      loading: Boolean,
      noDataText: {
        type: String,
        default: 'Нет данных для отображения. Пожалуйста, добавьте хотя бы одну группировку'
      }
    },
    computed: {
      noDataColor () {
        return this.loading ? 'rgba(0, 0, 0, 0.5)' : 'initial'
      }
    },
    methods: {
      closeMenus () {
        this.$refs.root.closeMenu()
      }
    }
  }
</script>

<style>
  .data-tree-root {
    list-style: none;
    align-self: flex-start;
  }

  .data-tree-root > li > ul {
    padding-left: 2px;
    background-image: none;
  }

  .data-tree-root > li > div > img {
    display: none;
  }

  .data-tree-loading {
    position: absolute;
    display: flex;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.05);
    align-items: center;
    justify-content: center;
  }

  .data-tree-btns {
    position: absolute;
    right: 0;
    top: 0;
  }

  .data-tree-container > div.title {
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
  }

  .data-tree-container {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    height: auto;
  }
</style>
