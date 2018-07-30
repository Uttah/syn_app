<template>
  <v-menu offset-y open-on-hover>
    <v-btn flat class="black--text" slot="activator">{{ menuItem.name }}</v-btn>
    <v-list>
      <v-list-tile v-for="item in menuItem.subItems" :key="item.label" :to="item.link">
        <v-list-tile-title>{{ item.label }}</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
</template>

<script>
  export default {
    name: 'TopMenuItem',
    props: ['menuItem']
  }
</script>
