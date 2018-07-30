<template>
  <notifications group="notification" position="bottom right" width="450px">
    <template slot="body" slot-scope="props">
      <div class="mb-3" :class="{ 'common-notification': props.item.text, 'error': !!(props.item.data && props.item.data.error),
       'warning': !!(props.item.data && props.item.data.warning), 'success': !!(props.item.data && props.item.data.success)}">
        <table width="100%">
          <tr>
            <td>
              <span class="title" @click="followLink(props.item.data.link, props.item.data.id, props)">
                <a style="color: white">{{ props.item.title }}</a>
              </span>
            </td>
            <td style="width: 30px;">
              <a class="close" @click="props.close(); confirmNotificationFunc(props.item.data.id)">
                <v-icon color="white">close</v-icon>
              </a>
            </td>
          </tr>
          <tr>
            <td colspan="2" @click="followLink(props.item.data.link, props.item.data.id, props)">
              <a style="color: white">
                <div class="mt-2" style="word-break: break-all;" v-html="props.item.text">
                </div>
              </a>
            </td>
          </tr>
        </table>
      </div>
    </template>
  </notifications>
</template>

<script>
  import {getNotice, confirmNotification} from './query'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'

  export default {
    name: 'get-notice',
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'network-only',
        pollInterval: 10000,
        query: getNotice,
        update (data) {
          window.notificationsDisplayed.forEach(id => {
            if (!data.getNotice.find(item => item.id === id)) {
              this.$notify({
                group: 'notification',
                clean: true
              })
              window.notificationsDisplayed = []
            }
          })
          if (data.getNotice.length > 0) {
            data.getNotice.forEach((item) => {
              if (window.notificationsDisplayed.length < 3 && window.notificationsDisplayed.find(item2 => item2 === item.id) === undefined) {
                this.$notify({
                  group: 'notification',
                  duration: -1,
                  title: 'От ' + item.created.shortName + ' (' + this.formatDateTime(item.date) + ')',
                  text: item.text,
                  data: {
                    id: item.id,
                    link: item.link,
                    success: item.type === 'S',
                    warning: item.type === 'W',
                    error: item.type === 'C'
                  }
                })
                window.notificationsDisplayed.push(item.id)
              }
            })
          }
        },
        skip () {
          return !this.auth.user.id || window.notificationsDisplayed.length >= 3
        }
      }
    },
    created () {
      window.notificationsDisplayed = []
    },
    data () {
      return {
        auth: auth
      }
    },
    methods: {
      followLink (link, id, props) {
        if (link) {
          props.close()
          window.open(link, '_blank')
          this.confirmNotificationFunc(id)
        }
      },
      confirmNotificationFunc (id) {
        this.$apollo.mutate({
          mutation: confirmNotification,
          variables: {
            input: {
              id: id
            }
          }
        })
        window.notificationsDisplayed = window.notificationsDisplayed.filter(idA => idA !== id)
      }
    }
  }
</script>

<style>

</style>
