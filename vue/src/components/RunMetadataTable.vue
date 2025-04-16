<template>
  <div>
    <b-table :data="table_data" :striped="true" detailed :show-detail-icon="false">
      <b-table-column field="is_custom" label="" align="center" v-slot="props" width="20">
        <span v-if="!props.row.is_custom" @click="props.toggleDetails(props.row)">
          <b-icon icon="information-outline" />
        </span>
      </b-table-column>

      <b-table-column field="k" label="" v-slot="props" width="300">
        <div @click="props.toggleDetails(props.row)">
          <b>{{ props.row.k }}</b>
        </div>
      </b-table-column>

      <b-table-column field="v" label="" v-slot="props">
        <div v-if="props.row.k.toLowerCase().includes('email')">
          <span v-if="verifiedEmails.includes(props.row.k)">
            {{ props.row.v }}
          </span>
          <span v-else-if="activeRecaptcha === props.row.k">
            <div :id="'recaptcha-container-' + props.row.k"></div>
          </span>
          <span v-else class="email-hidden" @click="showRecaptcha(props.row.k)">
            (hidden, click to reveal)
          </span>
        </div>
        <div v-else>
          {{ props.row.v }}
        </div>
      </b-table-column>

      <template #detail="props">
        <div v-if="props.row.is_custom">
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
import { verifyRecaptcha } from '@/api'
export default {
  name: 'RunMetadataTable',
  props: ['table_data'],
  data() {
    return {
      recaptchaSiteKey: '6LdZXhorAAAAAMxLgnqZRC7KQrTE-l1Sa4KLunJQ', // your reCAPTCHA site key
      verifiedEmails: [],                     // tracks verified email keys
      activeRecaptcha: null,                  // tracks the currently displayed reCAPTCHA
    };
  },
  methods: {
    verifyCallback(k, token) {
      // Immediately send token to backend
      verifyRecaptcha(token)
        .then(res => {
          if (res.data.success) {
            this.verifiedEmails.push(k);
          } else {
            alert('Verification failed. Try again.');
          }
          this.activeRecaptcha = null;
        })
        .catch(err => {
          console.error(err);
          alert('Verification error.');
          this.activeRecaptcha = null;
        });
    },
    showRecaptcha(k) {
      this.activeRecaptcha = k;
      this.$nextTick(() => {
        grecaptcha.render(`recaptcha-container-${k}`, {
          sitekey: this.recaptchaSiteKey,
          callback: (token) => this.verifyCallback(k, token),
          'expired-callback': () => (this.activeRecaptcha = null),
        });
      });
    },
  },
};
</script>

<style scoped>
.email-hidden {
  cursor: pointer;
  color: #007bff;
  text-decoration: underline;
}
.email-hidden:hover {
  color: #0056b3;
}
</style>
