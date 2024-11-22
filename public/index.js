import { createApp, ref } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
let lastMessage = ""

createApp({
    setup() {
        const shouldRender = ref(true); // Use ref to make it reactive
        const language = ref("en");

      function handleFlagClick(lang) {
        language.value = lang;
        shouldRender.value = false; // Update the value using `.value`
        }

        function returnHome() {
            shouldRender.value = true
        }
        
      return {
        handleFlagClick,
        shouldRender,
        returnHome,
        language
      }
    }
  }).mount('#app')