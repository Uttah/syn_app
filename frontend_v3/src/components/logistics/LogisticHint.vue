<template>
  <div>
    <div v-if="logisticRequest && isTransfer">
      <div v-if="position.transferpositionSet.length === 0" class="text-xs-center">-</div>
      <v-menu v-if="position.transferpositionSet.length !== 0" open-on-hover open-delay="300" top offset-y>
        <div slot="activator">
          <table>
            <tr>
              <td class="pl-0 pr-2" v-if="position.transferred">
                ({{ position.transferred }})
              </td>
              <td class="px-0">
                <template v-for="tp in position.transferpositionSet">
                  <div class="procurementWarning" v-if="!tp.transferRequest.readyToGo">
                    {{ tp.count + ' ' + tp.good.unit.shortName }}
                  </div>
                  <template v-if="tp.transferRequest.readyToGo">
                    <template v-if="tp.transferRequest.completed">
                      <div v-if="tp.count === tp.transferred">
                        {{ tp.count + ' ' + tp.good.unit.shortName }}
                      </div>
                      <div v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                        <del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}
                      </div>
                    </template>
                    <template v-else>
                      <div style="color: #8d8d8d" v-if="tp.transferred === null">
                        {{ tp.count + ' ' + tp.good.unit.shortName }}
                      </div>
                      <div style="color: #8d8d8d" v-if="tp.count === tp.transferred">
                        {{ tp.count + ' ' + tp.good.unit.shortName }}
                      </div>
                      <div style="color: #8d8d8d" v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                        <del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}
                      </div>
                    </template>
                  </template>
                </template>
              </td>
            </tr>
          </table>
        </div>
        <v-list v-for="tp in position.transferpositionSet" :key="tp.id" v-if="tp.transferRequest.readyToGo" class="ma-0 pa-0">
          <v-list-tile>
            <v-list-tile-title v-if="tp.transferRequest.readyToGo" style="height: 40px;">
              <template v-if="tp.transferRequest.completed">
                <template v-if="tp.count === tp.transferred">
                  {{ tp.count + ' ' + tp.good.unit.shortName }}
                </template>
                <template v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                  <del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}
                </template>
              </template>
              <template v-else>
                <template v-if="tp.transferred === null">
                  <span style="background: gray;">{{ tp.count + ' ' + tp.good.unit.shortName }}</span>
                </template>
                <template v-if="tp.count === tp.transferred">
                  <span style="background: gray;">{{ tp.count + ' ' + tp.good.unit.shortName }}</span>
                </template>
                <template v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                  <span style="background: gray;"><del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}</span>
                </template>
              </template>
              -
              <a target="_blank" :href="'/transfer_request/' + tp.transferRequest.id">заявка на перемещение №{{ tp.transferRequest.id }}</a>
              от
              <v-chip>
                <v-avatar>
                  <img :src="tp.transferRequest.whoRequested.avatar"/>
                </v-avatar>
                <span class="body-2">{{ tp.transferRequest.whoRequested.shortName }}</span>
              </v-chip>
            </v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-menu>
    </div>

    <div v-if="logisticDelivery && isTransfer">
      <v-menu open-on-hover open-delay="300" top offset-y>
        <div slot="activator" style="display: flex; height: 100%; align-items: center; justify-content: center">
          <span v-if="position.sumTransfer" style="padding-right: 5px">
            ({{position.sumTransfer}})
          </span>
          <div v-if="!position.sumTransfer && position.transferpositionSet.length === 0">
            -
          </div>
          <div>
            <template v-for="item in position.transferpositionSet">
              <div>
                <div v-if="item.transferRequest.completed === false && item.transferred !== item.count && item.transferred !== null" style="color: dimgray;" class="table-font-size">
                  <del style="color: red">{{ item.count }}</del>
                  {{' ' + item.transferred + ' ' + item.good.unit.shortName }}
                </div>
                <div v-else-if="item.transferRequest.completed === false" style="text-decoration: underline; color: dimgray;"
                     :class="{ new: item.transferRequest.readyToGo === false && item.transferRequest.completed === false}">
                  <span class="table-font-size">{{ item.count }} {{ item.good.unit.shortName }}</span>
                </div>
                <div v-else-if="item.transferRequest.completed === true && item.transferred != item.count" class="table-font-size">
                  <del style="color: red">{{ item.count }}</del>{{ ' ' + item.transferred + ' ' + item.good.unit.shortName }}
                </div>
                <div v-else-if="item.transferRequest.completed === true && item.transferred >= item.count"
                     style="text-decoration: underline;" class="table-font-size">
                  {{ item.count }} {{ item.good.unit.shortName }}
                </div>
              </div>
            </template>
          </div>
        </div>
        <!--Всплывающая подсказка-->
        <v-list v-for="tp in position.transferpositionSet" :key="tp.id" v-if="position.sumTransfer && tp.transferRequest.readyToGo" class="ma-0 pa-0">
          <v-list-tile>
            <v-list-tile-title style="height: 40px;">
              <template v-if="tp.transferRequest.completed">
                <template v-if="tp.count === tp.transferred">
                  {{ tp.count + ' ' + tp.good.unit.shortName }}
                </template>
                <template v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                  <del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}
                </template>
              </template>
              <template v-else>
                <template v-if="tp.transferred === null">
                  <span style="background: gray;">{{ tp.count + ' ' + tp.good.unit.shortName }}</span>
                </template>
                <template v-if="tp.count === tp.transferred">
                  <span style="background: gray;">{{ tp.count + ' ' + tp.good.unit.shortName }}</span>
                </template>
                <template v-if="tp.transferred > -1 && tp.transferred !== null && tp.count !== tp.transferred">
                  <span style="background: gray;"><del class="del">{{ tp.count }}</del>{{ ' ' + tp.transferred +  ' ' + tp.good.unit.shortName }}</span>
                </template>
              </template>
              -
              <a target="_blank" :href="'/transfer_request/' + tp.transferRequest.id">заявка на перемещение №{{ tp.transferRequest.id }}</a>
              от
              <v-chip>
                <v-avatar>
                  <img :src="tp.transferRequest.whoRequested.avatar"/>
                </v-avatar>
                <span class="body-2">{{ tp.transferRequest.whoRequested.shortName }}</span>
              </v-chip>
            </v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-menu>
    </div>

    <div v-if="!isTransfer">
      <div v-if="position.inStock.length === 0" class="text-xs-center">-</div>
      <v-menu open-on-hover open-delay="300" top offset-y>
        <div slot="activator" @mouseover="sendQueries">
          <span v-if="position.inStock.length > 0 && position.inStock[0].unit.restrictSum" v-html="createInStockForUnitsWithRestrictSumTrue(position.count, position.unit.id, position.inStock)"></span>
          <div v-for="is in position.inStock" v-if="position.inStock.length > 0 && !position.inStock[0].unit.restrictSum">
            <span style="color: #0d47a1" v-if="is.unit.id === position.unit.id">
              <template v-if="is.available !== 0 && is.available !== is.count || is.available === 0 && is.count !== 0">
                {{ is.available + ' (' + is.count + ') ' + is.unit.shortName }}
              </template>
              <template v-if="is.available === is.count && is.available !== 0 && is.count !== 0">
                {{ is.count + ' ' + is.unit.shortName }}
              </template>
            </span>
            <span style="color: #8d8d8d" v-if="is.unit.id !== position.unit.id">
              <template v-if="is.available !== 0 && is.available !== is.count">
                {{ is.available + ' (' + is.count + ') ' + is.unit.shortName }}
              </template>
              <template v-if="is.available === 0 || is.available === is.count && is.count !== 0">
                {{ is.count + ' ' + is.unit.shortName }}
              </template>
            </span>
          </div>
        </div>
        <v-list v-for="trpi in transferRequestPositionInfoData" :key="trpi.id" class="ma-0 pa-0">
          <v-list-tile>
            <v-list-tile-title v-if="trpi.readyToGo" style="height: 40px;">
              {{ trpi.count }} - <a target="_blank" :href="'/transfer_request/' + trpi.id">заявка на перемещение №{{ trpi.id }}</a>
              от
              <v-chip>
                <v-avatar>
                  <img :src="trpi.whoRequested.avatar"/>
                </v-avatar>
                <span class="body-2">{{ trpi.whoRequested.shortName }}</span>
              </v-chip>
            </v-list-tile-title>
            <v-list-tile-title v-if="!trpi.readyToGo" style="height: 40px;">{{ trpi.count }} - зарезервировано
              у
              <v-chip>
                <v-avatar>
                  <img :src="trpi.whoRequested.avatar"/>
                </v-avatar>
                <span class="body-2">{{ trpi.whoRequested.shortName }}</span>
              </v-chip>
            </v-list-tile-title>
          </v-list-tile>
        </v-list>

        <template v-for="is in position.inStock" v-if="is.unit.id === position.unit.id">
          <v-list v-if="is.available !== 0" class="ma-0 pa-0">
            <v-list-tile>
              <v-list-tile-title style="height: 28px;">
                <span :style="{background: is.available >= position.count ? '#00c853' : 'initial'}">{{ is.available + ' ' + is.unit.shortName }}</span> - основной склад
              </v-list-tile-title>
            </v-list-tile>
          </v-list>
          <!--<div v-if="is.available !== 0" class="pa-2" style="height: 28px;">-->
          <!--<span style="background: #00c853">{{ is.available + ' ' + is.unit.shortName }}</span> - основной склад-->
          <!--</div>-->
        </template>

        <template v-for="gli in goodLocationInfoData">
          <v-list v-if="goodLocationInfoData.length > 0" class="ma-0 pa-0">
            <v-list-tile>
              <v-list-tile-title style="height: 40px;">
                {{ gli.good.count + ' ' + gli.good.unit.shortName + ' склад, проект ' + formatProject(gli.project.number) + ', ГИП '}}
                <v-chip>
                  <v-avatar>
                    <img :src="gli.project.gip.avatar"/>
                  </v-avatar>
                  <span class="body-2">{{ gli.project.gip.shortName }}</span>
                </v-chip>
              </v-list-tile-title>
            </v-list-tile>
          </v-list>
        </template>
      </v-menu>
    </div>
  </div>
</template>

<script>
  import utilsMixin from '../utils'
  import {transferRequestPositionInfo, goodLocationInfo} from './query'

  export default {
    name: 'logisticHint',
    props: {
      position: Object,
      logisticDelivery: {
        type: Boolean,
        default: false
      },
      logisticRequest: {
        type: Boolean,
        default: false
      },
      isTransfer: {
        type: Boolean,
        default: false
      }
    },
    mixins: [utilsMixin],
    data () {
      return {
        transferRequestPositionInfoData: [],
        goodLocationInfoData: []
      }
    },
    methods: {
      createInStockForUnitsWithRestrictSumTrue (requested, requestedUnitId, inStock) {
        let result = ''
        let value = false
        inStock.forEach((is, i) => {
          if (is.available > 0) {
            let color = '#8d8d8d'
            if (is.available >= requested && is.unit.id === requestedUnitId) {
              value = true
              color = '#0d47a1'
            }
            const comma = (i < inStock.length - 1) ? ',' : ''
            result += `<span style="color: ${color}">${is.available}${comma} </span>`
          }
        })
        // Проверка есть ли позиции на других складах и проектах(Для отображения скобок)
        let isContains = inStock.some(is => {
          if (is.available === 0) {
            return true
          }
        })
        // Если есть позиции в скобках - сортируем по возрастанию и выводим
        if (isContains) {
          let sortedArray = []
          inStock.forEach(is => {
            if (is.available === 0) {
              sortedArray.push(is.count)
            }
          })
          sortedArray.sort((a, b) => a - b)
          result = result.slice(0, -9) + '</span> ('
          sortedArray.forEach(sa => {
            result += sa + ', '
          })
          result = result.slice(0, -2) + ') '
        }
        if (value) {
          result += '<span style="color: #0d47a1">' + inStock[0].unit.shortName + '</span>'
        } else {
          result += '<span style="color: #8d8d8d">' + inStock[0].unit.shortName + '</span>'
        }
        return result
      },
      sendQueries () {
        this.$apollo.query({
          fetchPolicy: 'network-only',
          query: transferRequestPositionInfo,
          variables: {
            positionId: this.position.id
          }
        }).then(({data}) => {
          this.transferRequestPositionInfoData = data.transferRequestPositionInfo
        })
        this.$apollo.query({
          fetchPolicy: 'network-only',
          query: goodLocationInfo,
          variables: {
            positionId: this.position.id
          }
        }).then(({data}) => {
          this.goodLocationInfoData = data.goodLocationInfo
        })
      }
    }
  }
</script>
