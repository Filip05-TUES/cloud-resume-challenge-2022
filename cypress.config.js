const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL,

    env: {
      apiUrl: process.env.CYPRESS_API_URL,
    },
  },
});