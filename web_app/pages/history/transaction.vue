<template>
  <div class="transaction">
    <div v-if="transactionData" class="not-session">
      <h2 class="title">У&nbsp;вас&nbsp;еще&nbsp;не&nbsp;было транзакций</h2>
      <h3 class="title">После&nbsp;завершения каждой&nbsp;сессии&nbsp;они будут&nbsp;показанны в&nbsp;этом&nbsp;окне.</h3>
    </div>

    <div class="box-transaction" :class="{ 'border-color': transac.status !== 'ACT' }" v-for="transac in transaction"
      :key="transac.uuid">
      <div class="title-box">
        <span class="date">{{ getDate(transac.created_at)[0] }}</span>
        <span class="pay" :class="transac.status">{{ transac.cost_total }} <span class="money"></span> </span>
        <span class="status" :class="transac.status">{{ statusPay[transac.status] }}</span>
      </div>
    </div>
    <Loading :loading="!transactionData && !transaction.length > 0" />
  </div>
</template>

<script leng="js">
export default {
  name: 'TransactionPage',
  data: () => ({
    statusPay: {
      PENDING: 'Платеж инициализирован',
      PAID: 'Платеж оплачен',
      CANCELED: 'Платеж отменен',
      REFUNDED: 'Платеж возращен'
    },
    history: [1],
  }),
  computed: {
    transaction() {
      return this.$store.state.transaction || []
    },
    transactionData() {
      return this.$store.state.transactionData
    },
  },
  methods: {
    getDate(timestamp) {
      let date = new Date(timestamp * 1000).toLocaleString([], { year: 'numeric', month: 'numeric', day: 'numeric' }),
        time = new Date(timestamp * 1000).toLocaleString([], { hour: '2-digit', minute: '2-digit' })
      return [date, time];
    },
  },
}
</script>

<style lang="scss" scoped>
.transaction {
  padding-top: 40px;
  text-align: center;
  font-family: "myriadRegular";

  .box-transaction {
    margin: 0 auto 10px;
    width: 90%;
    background-color: var(--white-text);
    border: 2px solid var(--blue);
    border-radius: 10px;


    .title-box {
      width: calc(100% - 24px);
      margin: 0 0 0 -2px;
      background: var(--white-text);
      color: var(--black-text);
      padding: 10px 12px;
      font-style: normal;
      font-weight: 400;
      line-height: 20px;
      font-size: .9em;
      display: flex;
      justify-content: space-between;
      border-radius: 10px;
      border-left: 2px solid var(--blue);
      border-right: 2px solid var(--blue);
      cursor: pointer;

      .date {
        flex-basis: 20%;
        color: #575756;
      }

      .pay {
        flex-basis: 10%;
        display: flex;
        position: relative;
      }

      .status {
        font-size: .8em;
        flex-basis: 40%;
      }

      .PENDING {
        color: #64cb9b;
        font-weight: bold;
      }

      .PAID {
        color: #00A658;
        font-weight: bold;
      }

      .REFUNDED {
        color: #E52A12;
        font-weight: bold;
      }

      .CANCELED {
        color: #f7b40a;
        font-weight: bold;
      }
    }
  }
}</style>
