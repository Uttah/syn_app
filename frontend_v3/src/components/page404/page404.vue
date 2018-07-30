<template>
  <v-card>
    <v-card-media :src="travolta" height="500px" contain>
      <v-container fluid style="height: 100%" class="pa-4">
        <v-layout>
          <v-flex xs6>
            <span class="headline">Запрашиваемая страница не найдена</span>
          </v-flex>
        </v-layout>
      </v-container>
    </v-card-media>
  </v-card>
</template>

<script>
  import travolta from '../../assets/404_travolta.gif'

  export default {
    name: 'page404',
    metaInfo: {
      title: 'Страница не найдена'
    },
    data () {
      return {
        travolta: travolta
      }
    }
  }
</script>
