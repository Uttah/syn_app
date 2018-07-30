<template>
  <logging
    model-name="users.Occupation"
    title="История изменений финансовой информации сотрудников"
    :instance-id="occupationId"
    :back-btn-route="{name: 'financial_info'}"
    back-btn-title="Назад к финансовой информации пользователей"
  >
    <occupation-filter slot="filter" v-model="occupationId" clearable style="max-width: 350px"/>
  </logging>
</template>

<script>
  import Logging from '../logging/Logging'
  import OccupationFilter from './OccupationFilter'

  export default {
    components: {
      OccupationFilter,
      Logging
    },
    name: 'financial-info-history',
    data () {
      return {
        occupationId: null
      }
    }
  }
</script>
