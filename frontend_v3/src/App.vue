<template>
  <v-app light>
    <div>
      <top-menu v-if="showMenu"/>
      <alarms ref="alarms"/>
      <notice/>
      <notifications group="commonNotification" :max="1" position="top right" width="450px">
        <template slot="body" slot-scope="props">
          <div class="mb-1 common-notification" :class="{'error': !!(props.item.data && props.item.data.error),
          'warning': !!(props.item.data && props.item.data.warning), 'success': !!(props.item.data && props.item.data.success)}">
            <table width="100%">
              <tr>
                <td class="subheading">
                  <span v-if="!(props.item.data && props.item.data.error)">Уведомление</span>
                  <span v-if="!!(props.item.data && props.item.data.error)">Ошибка</span>
                </td>
                <td style="width: 30px">
                  <a class="close" @click="props.close()" title="Закрыть">
                    <v-icon color="white">close</v-icon>
                  </a>
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <div class="mt-2" style="word-break: break-all" v-html="props.item.text"></div>
                </td>
              </tr>
            </table>
          </div>
        </template>
      </notifications>
      <router-view/>
    </div>
  </v-app>
</template>

<script>
  import TopMenu from './components/menu/TopMenu.vue'
  import Alarms from './components/Alarms.vue'
  import Notice from './components/notice/GetNotice.vue'

  export default {
    name: 'App',
    components: {
      TopMenu,
      Alarms,
      Notice
    },
    computed: {
      showMenu: function () {
        return this.$route.name !== 'login'
      }
    }
  }
</script>

<style lang="stylus">
  html {
    overflow-y: auto !important;
  }

  tr.locked, tr.deleted, tr.fired, tr.checked, tr.new {
    border-bottom: 1px solid rgba(0, 0, 0, .12) !important;
  }

  tr.locked:hover, tr.deleted:hover, tr.fired:hover, tr.checked:hover, tr.new:hover {
    background-color: rgba(0, 0, 0, .06) !important;
  }

  .common-notification {
    padding: 10px;
    margin: 5px;

    color: #ffffff;
    background: rgba(33, 33, 33, .8);
    border-left: 5px solid #212121;
  }

  .common-notification.error {
    background: rgba(183, 28, 28, .8) !important;
    border-left: 5px solid #b71c1c;
  }

  .common-notification.warning {
    background: rgba(168, 184, 0, .8) !important;
    border-left: 5px solid #b71c1c;
  }

  .common-notification.success {
    background: rgba(0, 179, 0, .8) !important;
    border-left: 5px solid #b71c1c;
  }
</style>
