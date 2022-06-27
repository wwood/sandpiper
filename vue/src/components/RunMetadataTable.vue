<template>
  <div>
        <b-table :data="table_data" :striped="true" detailed :show-detail-icon="false">
          <b-table-column field="is_custom" label="" align="centre" v-slot="props" width="20">
            <span v-if="!props.row.is_custom" @click="props.toggleDetails(props.row)"><b-icon icon="information-outline" /></span>
          </b-table-column>
          <b-table-column field="k" label="" v-slot="props" width="300">
            <div @click="props.toggleDetails(props.row)"><b>{{ props.row.k }}</b></div>
          </b-table-column>
          <b-table-column field="v" label="" v-slot="props" >
            {{ props.row.v }}
          </b-table-column>
          <template #detail="props">
            <div v-if="props.row.is_custom === true">
              "{{props.row.k}}" is a custom attribute that is not defined by NCBI.
            </div>
            <div v-else>
              "{{props.row.k}}" is {{props.row.description}}
            </div>
          </template>
        </b-table>
  </div>
</template>

<script>

export default {
  name: 'RunMetadataTable',
  props: ['table_data'],
}
</script>
