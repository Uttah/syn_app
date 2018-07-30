<template>
  <v-menu
    ref="menu"
    lazy
    :close-on-content-click="false"
    v-model="menu"
    :disabled="disabled || readonly"
    full-width
  >
    <v-text-field
      slot="activator"
      :label="label"
      v-model="formattedValue"
      :prepend-icon="prependIcon"
      :rules="rules"
      readonly
      :disabled="disabled"
    />
    <v-time-picker v-model="innerValue" autosave format="24hr" @change="$refs.menu.save(innerValue)"/>
  </v-menu>
</template>

<script>
  export default {
    name: 'time-picker',
    props: {
      disabled: Boolean,
      label: String,
      prependIcon: String,
      readonly: Boolean,
      rules: Array,
      value: String
    },
    data () {
      return {
        innerValue: this.value,
        menu: false
      }
    },
    watch: {
      value (newValue) {
        this.innerValue = newValue
      },
      innerValue (newValue) {
        this.$emit('input', newValue)
      }
    },
    computed: {
      formattedValue () {
        if (this.innerValue) {
          return this.innerValue.substr(0, 5)
        } else {
          return ''
        }
      }
    }
  }
</script>

<style scoped>

</style>
