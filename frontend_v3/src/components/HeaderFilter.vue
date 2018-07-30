<template>
  <v-menu lazy :close-on-content-click="false" transition="scale-transition"
          offset-y max-width="400px" min-width="400px" content-class="whiteback">
    <v-btn flat :outline="filterApplied" :color="filterApplied ? 'accent' : ''" style="display: inline"
           slot="activator">
      <v-icon :style="{transform: 'rotate(' + rotation + 'deg)', transition: 'transform 0.5s linear'}">filter_list
      </v-icon>
      Фильтр
    </v-btn>
    <v-container fluid class="pa-1" style="margin-bottom: -35px">
      <v-btn icon style="margin-left: 90%; z-index: 2" @click="$emit('clearFilters')" title="Очистить фильтры">
        <v-icon>clear_all</v-icon>
      </v-btn>
      <div style="position: relative; top: -40px">
        <slot>
        </slot>
      </div>
    </v-container>
  </v-menu>
</template>

<script>
  export default {
    name: 'HeaderFilter',
    data () {
      return {
        menu: false,
        filterApplied: false,
        rotation: 0,
        appliedFilters: {}
      }
    }
  }
</script>

<style>
  .whiteback {
    background-color: white;
    overflow: hidden;
  }
</style>
