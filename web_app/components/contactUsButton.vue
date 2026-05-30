<template>
  <CustomButton @get="reportProblem" value="Сообщить о проблеме!" type="attention" classList="report-problem-button" />
</template>

<script>
import CustomButton from "~/components/customButton.vue";

export default {
  name: "ContactUsButton",
  components: {
    CustomButton,
  },
  methods: {
    reportProblem() {
      if (process.env.REPORT_PROBLEM_URL && process.env.REPORT_PROBLEM_URL != '') {
        window.location.assign(process.env.REPORT_PROBLEM_URL);
      }
    },
  },
};

</script>

<style></style>
