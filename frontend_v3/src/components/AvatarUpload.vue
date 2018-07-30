<template>
  <vue-dropzone
    ref="dropzone"
    id="dropzone"
    name="drop"
    :options="dropzoneOptions"
    @vdropzone-sending="beforeSending"
    @vdropzone-success="success"
    :style="dzBackground"
  />
</template>

<script>
  import vue2Dropzone from 'vue2-dropzone'
  import 'vue2-dropzone/dist/vue2Dropzone.css'
  import Cookie from 'js-cookie'

  const production = process.env.NODE_ENV === 'production'

  export default {
    name: 'AvatarUpload',
    props: {
      mutate: Object,
      variables: Object,
      maxFilesize: {
        type: Number,
        default: 2
      },
      extractPath: Function,
      value: String
    },
    components: {
      vueDropzone: vue2Dropzone
    },
    data () {
      return {
        dropzoneOptions: {
          url: this.appendDebugServer('/api_v1'),
          acceptedFiles: '.jpg,.jpeg,.png',
          withCredentials: true,
          maxFilesize: this.maxFilesize,
          maxFiles: 1,
          dictDefaultMessage: '',
          headers: {
            'X-CSRFToken': Cookie.get('csrftoken') || null
          },
          previewTemplate: `<template></template>`
        },
        uploadedResult: this.value
      }
    },
    methods: {
      beforeSending (file, xhr, formData) {
        formData.append('operationName', null)
        formData.append('variables', JSON.stringify({input: this.variables}))
        formData.append('query', this.mutate.loc.source.body)
      },
      success (file, response) {
        // В продакшене нам отвечают батчем, так что нужно получать свой элемент из массива
        const data = production ? response[0].data : response.data
        this.$emit('input', this.extractPath(data))
        // Удаляем файлы из дропзоны, так как они отображаются в бекграунде
        this.$refs.dropzone.removeAllFiles()
      },
      appendDebugServer (value) {
        return (production ? '' : '//localhost:8000') + value
      }
    },
    computed: {
      dzBackground () {
        if (!this.uploadedResult) {
          return {}
        } else {
          return {
            background: `url(${this.uploadedResult}) center/contain no-repeat`
          }
        }
      }
    },
    watch: {
      value (newVal) {
        this.uploadedResult = this.appendDebugServer(newVal)
      }
    }
  }
</script>
