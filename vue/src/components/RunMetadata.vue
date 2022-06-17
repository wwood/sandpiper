<template>
<div>
<div class="container">
<section>
      <h3 class="title">General metadata</h3>
      <b-table :data="gatherMetadata ('general')" :columns="generalMetadataColumns()" :striped="true" />
</section>
</div>

&nbsp;
<div class="container">
<section>
      <h3 class="title">BioSample metadata</h3>
      <b-table :data="mdata.biosample_attributes" :columns="column_definition()" :striped="true" />
</section>
</div>

&nbsp;
<div class="container">
<section>
      <h3 class="title">Parsed metadata</h3>
      <b-table :data="gatherMetadata ('parsed_sample_attributes')" :columns="generalMetadataColumns()" :striped="true" />
</section>
</div>

&nbsp;
<div class="container">
<section>
      <h3 class="title">Study links</h3>
      <div v-if="Object.keys(gatherMetadata ('study_links')).length===0">
        <p>No linked studies recorded</p>
      </div>
      <div v-else>
        <b-table :data="gatherMetadata ('study_links')" :columns="studyLinksColumns()" :striped="true" />
      </div>
</section>
</div>

</div>
</template>

<script>

export default {
  name: 'RunMetadata',
  props: ['mdata'],
  methods: {
    // Data to be put in the general metadata
    gatherMetadata (section) {
      const toReturn = []
      Object.keys(this.mdata).forEach(key => {
        const v = this.mdata[key]
        if (section==='general') {
          if (key !== 'biosample_attributes' && key !== 'study_links' && key !== 'parsed_sample_attributes' && v !== null) {
            toReturn.push({
              k: key,
              value: v
            })
          }
        } else if (section==='study_links' && key === 'study_links') {
          v.forEach(link => {
            if (typeof link['database'] !== 'undefined') {
              if (link['database'].toLowerCase() === 'pubmed'){
                toReturn.push({
                  k: link['database'],
                  value: '<a href="https://www.ncbi.nlm.nih.gov/pubmed?term='+link['study_id']+'">'+link['study_id']+'</a>'
                })
              } else {
                toReturn.push({
                  k: link['database'],
                  value: link['study_id']
                })
              }
            } else {
              toReturn.push({
                k: link.label,
                value: '<a href="'+link.url+'">'+link.url+'</a>'
              })
            }
          })
        } else {
          if (key === section) {
            Object.keys(v).forEach(k => {
              if (v[k] !== null) {
                toReturn.push({
                  k: k,
                  value: v[k]
                })
              }
            })
          }
        }
      })
      return toReturn
    },
    generalMetadataColumns () {
      return [{ label: 'attribute', field: 'k' }, { label: 'value', field: 'value' }]
    },
    studyLinksColumns () {
      return [{ label: 'database', field: 'k' }, { label: 'id', field: 'value' }]
    },
    column_definition () {
      return [{ label: 'attribute', field: 'k', align: 'center' }, { label: 'value', field: 'v' }]
    }
  },
  data () {
    return {
      medata: this.mdata
    }
  }
}
</script>
