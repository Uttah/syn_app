<template>
  <div ref="root" id="file-upload-dz" class="file-upload">
    <div v-if="!readOnly" class="caption rotated" :style="captionDims" ref="caption">{{ caption }}</div>
    <div class="preview-container" ref="dzRoot" :style="containerStyle">
      <div class="file-preview" :style="previewStyle" v-for="item in uploadedResult">
        <v-btn flat small icon color="red" title="Удалить файл" size="20px" class="del-btn"
               v-if="clickable" @click="deleteFile(item)">
          <v-icon size="18px">clear</v-icon>
        </v-btn>
        <a :href="appendDebugServer(`/download/?kind=${item.kind}&id=${item.id}`)" target="_blank">
          <img :src="fileIcon" :style="imgStyle" :title="readOnly ? item.name : null">
          <div v-if="!readOnly">{{ item.name }}</div>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
  import Dropzone from 'dropzone'
  import fileIcon from '../assets/file-icon.png'
  import Cookie from 'js-cookie'

  const production = process.env.NODE_ENV === 'production'

  export default {
    name: 'FileUpload',
    props: {
      mutate: Object,
      variables: Object,
      delMutation: Object,
      delVariables: {
        type: Object,
        default: () => {
          return {}
        }
      },
      readResultFromData: Function,
      maxFilesize: {
        type: Number,
        default: 2
      },
      maxNumFiles: {
        type: Number,
        default: null
      },
      caption: {
        type: String,
        default: 'Документы'
      },
      clickable: {
        type: Boolean,
        default: true
      },
      extractPath: Function,
      value: Array,
      readOnly: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        dropzoneOptions: {
          url: this.appendDebugServer('/api_v1'),
          withCredentials: true,
          maxFilesize: this.maxFilesize,
          maxFiles: this.maxNumFiles,
          clickable: true,
          dictDefaultMessage: '',
          headers: {
            'X-CSRFToken': Cookie.get('csrftoken') || null
          },
          previewTemplate: '<template></template>'
        },
        dz: null,
        uploadedResult: this.value,
        showDropText: false,
        captionDims: {
          width: 'initial',
          top: '50%',
          left: '50%',
          containerHeight: '100%'
        },
        fileIcon: fileIcon
      }
    },
    mounted () {
      this.$nextTick(() => this.updateDims())
      this.createDropzone()
    },
    methods: {
      createDropzone () {
        this.dz = new Dropzone(this.$refs.dzRoot, this.dropzoneOptions)
        if (!this.clickable || !this.canUpload) {
          this.dz.disable()
        }
        this.dz.on('success', (file, response) => {
          this.success(file, response)
        })
        this.dz.on('sending', (file, xhr, formData) => {
          this.beforeSending(file, xhr, formData)
        })
      },
      beforeSending (file, xhr, formData) {
        formData.append('operationName', null)
        formData.append('variables', JSON.stringify({input: this.variables}))
        formData.append('query', this.mutate.loc.source.body)
      },
      success (file, response) {
        // В продакшене нам отвечают батчем, так что нужно получать свой элемент из массива
        const data = production ? response[0].data : response.data
        this.$emit('input', this.extractPath(data))
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: `Файл "${file.name}" загружен`
        })
      },
      appendDebugServer (value) {
        return (production ? '' : '//localhost:8000') + value
      },
      updateDims () {
        const containerHeight = this.$refs.root.clientHeight
        this.captionDims.containerHeight = (containerHeight - 2) + 'px'
        if (!this.readOnly) {
          const width = this.$refs.caption.clientWidth + 10
          this.captionDims.width = width - 2 + 'px'
          this.captionDims.left = '-' + width / 2 + 'px'
          this.captionDims.top = (containerHeight - this.$refs.caption.clientHeight) / 2 + 'px'
        }
      },
      deleteFile (file) {
        const input = JSON.parse(JSON.stringify(this.delVariables))
        input.id = file.id
        input.kind = file.kind
        this.$apollo.mutate({
          mutation: this.delMutation,
          variables: {
            input: input
          }
        }).then(({data}) => {
          if (this.readResultFromData(data)) {
            this.uploadedResult = this.uploadedResult.filter(item => item.id !== file.id)
            this.$emit('input', this.uploadedResult)
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: `Файл "${file.name}" удалён`
            })
          }
        })
      }
    },
    computed: {
      imgStyle () {
        return {
          height: this.readOnly ? '95%' : '60%',
          width: this.readOnly ? '95%' : '60%'
        }
      },
      previewStyle () {
        const w = this.readOnly ? '30px' : '75px'
        return {
          'min-width': w,
          'max-width': w,
          height: w
        }
      },
      containerStyle () {
        const cursor = this.readOnly ? 'default' : (this.clickable && this.canUpload ? 'copy' : 'no-drop')
        return {
          height: this.captionDims.containerHeight,
          cursor: cursor
        }
      },
      canUpload () {
        return this.value.length < this.maxNumFiles
      }
    },
    watch: {
      value (newVal) {
        this.uploadedResult = newVal
        this.$nextTick(() => {
          if (this.canUpload) {
            this.dz.enable()
          } else {
            this.dz.disable()
          }
        })
      },
      clickable (newVal) {
        if (!newVal) {
          this.dz.disable()
        } else {
          this.dz.enable()
        }
      }
    }
  }
</script>

<style>
  #file-upload-dz {
    border: 1px dashed black;
  }

  .file-upload {
    position: relative;
  }

  .file-upload div.caption.rotated {
    text-align: center;
    position: absolute;
    transform: rotate(-90deg);
    transform-origin: center center;
    background-color: white;
    border-radius: 11px;
    z-index: 2;
  }

  #file-upload-dz {
    padding: 0;
    min-height: 125px;
  }

  #file-upload-dz .file-preview {
    margin: 5px 10px;
    text-align: center;
    position: relative;
  }

  #file-upload-dz .file-preview .del-btn {
    position: absolute;
    right: -5px;
    top: -12px;
    margin: 0;
  }

  #file-upload-dz .file-preview > a > div {
    font-size: 9px;
    line-height: normal;
    word-break: break-all;
  }

  #file-upload-dz .preview-container {
    width: 100%;
    display: flex;
    justify-content: left;
    align-items: center;
    overflow-x: auto;
  }
</style>
