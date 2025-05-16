const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on('task', {
        log(message) {
          console.log(message)
          return null
        },
      })
      },
        baseUrl: 'http://localhost:3000'
  },

    component: {
      devServer: {
        framework: "create-react-app",
        bundler: "webpack",
      },
    },
  });
