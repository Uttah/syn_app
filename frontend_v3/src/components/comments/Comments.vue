<template>
  <div class="comments">
    <v-toolbar v-if="head">
      <v-toolbar-title>Комментарии</v-toolbar-title>
    </v-toolbar>
    <v-list id="list" style="max-height: 450px; overflow-y: auto;">
      <div class="pb-2" v-for="c in commentsData">
        <div class="comment-head">
          <v-avatar size="40px">
            <img :src="formatURL(c.user.avatar)">
          </v-avatar>
          <span class="subheader shrink-font">{{ c.user.shortName }} {{ formatDateTime(c.date) }}</span>
          <v-spacer/>
        </div>
        <div class="mt-2" style="word-break: break-all;">
          {{ c.comment }}
        </div>
        <v-divider class="mt-2"/>
      </div>
    </v-list>
    <v-select
      class="px-2"
      placeholder="Для кого"
      chips
      multiple
      autocomplete
      clearable
      hide-details
      v-model="targetsComment"
      :items="allUsersData"
      item-text="shortName"
      item-value="id"
    >
      <template slot="selection" slot-scope="data">
        <v-chip
          close
          @input="removeTarget(data.item.id)"
          :selected="data.selected"
        >
          <v-avatar>
            <img :src="data.item.avatar">
          </v-avatar>
          <span>{{ data.item.shortName }}</span>
        </v-chip>
      </template>
    </v-select>
    <v-text-field class="px-2 pt-2"
                  v-model="comment"
                  :error-messages="commentError"
                  multi-line
                  placeholder="Введите комментарий"
    />
    <div class="text-xs-right">
      <v-btn color="submit" :loading="loading" @click="createCommentFunc">Отправить</v-btn>
    </div>
  </div>
</template>

<script>
  import gql from 'graphql-tag'
  import {comments, createComment} from './query'
  import utilMixin from '../utils'

  export default {
    name: 'comments',
    props: {
      name: String,
      objectId: Number,
      head: {
        type: Boolean,
        default: false
      }
    },
    mixins: [utilMixin],
    apollo: {
      getComments: {
        fetchPolicy: 'network-only',
        pollInterval: 10000,
        query: comments,
        variables () {
          return {
            name: this.name,
            objectId: this.objectId
          }
        },
        update (data) {
          this.commentsData = data.comments
          this.scrollBottom = false
        }
      },
      query2: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            allUsers {
              id
              shortName
              avatar
            }
          }`,
        update (data) {
          this.allUsersData = data.allUsers
        }
      }
    },
    updated () {
      if (!this.scrollBottom) {
        let list = window.document.getElementById('list')
        list.scrollTop = list.scrollHeight
        this.scrollBottom = true
      }
    },
    data () {
      return {
        loading: false,
        scrollBottom: false,
        commentsData: [],
        allUsersData: [],
        targetsComment: [],
        comment: '',
        commentError: []
      }
    },
    methods: {
      removeTarget (id) {
        this.targetsComment = this.targetsComment.splice(this.targetsComment.indexOf(id), 1)
      },
      createCommentFunc () {
        if (!this.comment) {
          this.commentError = 'Нужно ввести текст'
          return
        }
        this.loading = true
        this.$apollo.mutate({
          mutation: createComment,
          variables: {
            input: {
              name: this.name,
              objectId: this.objectId,
              comment: this.comment,
              targets: this.targetsComment
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$apollo.queries.getComments.refetch()
          this.comment = ''
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      comment (val) {
        if (val) {
          this.commentError = []
        }
      }
    }
  }
</script>

<style>
  .comments {
    width: 600px;
  }

  .comments .comment-head {
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }

  .comments .shrink-font {
    line-height: 1;
    height: auto;
    padding-left: 10px;
  }
</style>
