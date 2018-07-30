<template>
  <span>
    <v-chip class="userWrapperClass ma-0" v-if="users && users.length < 2" v-for="r in users" :key="r.id">
      <v-avatar class="mr-0">
        <img :src="r.avatar"/>
      </v-avatar>
      <span>{{ r.shortName }}</span>
    </v-chip>

    <span class="userWrapperClass" v-if="users && users.length >= 2 && users.length < 4" style="margin-right: 15px">
      <v-chip v-for="r in users" :key="r.id" style="margin-right: -15px">
        <v-avatar class="mr-0">
          <img :src="formatURL(r.avatar)"/>
        </v-avatar>
        <span class="userNameWrapper">
          <span class="userNameClass">{{ r.shortName }}</span>
        </span>
      </v-chip>
    </span>

    <span class="userWrapperClass" v-if="users && users.length >= 4" style="margin-right: 15px">
      <v-chip v-for="r in users" :key="r.id" style="margin-right: -15px">
        <v-avatar class="mr-0" :title="r.shortName">
          <img :src="formatURL(r.avatar)"/>
        </v-avatar>
      </v-chip>
    </span>
  </span>
</template>

<script>
  import utilsMixin from './utils'

  export default {
    name: 'usersChip',
    mixins: [utilsMixin],
    props: {
      users: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        usersData: this.users
      }
    }
  }
</script>

<style>
  .userWrapperClass .chip .chip__content {
    padding-right: 0px !important;
    height: 25px;
  }

  .userNameWrapper{
    width: 0;
    overflow: hidden;
  }

  .chip:hover .userNameWrapper{
    width: 100%;
  }

  .userNameClass {
    overflow: hidden;
  }
</style>
