import {
  createApp,
  ref,
} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
let lastMessage = "";

createApp({
  setup() {
    const shouldRender = ref(true); // Use ref to make it reactive
    const language = ref("en");

    function handleFlagClick(lang) {
      language.value = lang;
      shouldRender.value = false; // Update the value using `.value`
    }

    function returnHome() {
      shouldRender.value = true;
    }
    function takePicture() {
      // Send POST request to capture image
      fetch("/capture_image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            alert("Failed to capture image: " + data.error);
          } else {
            alert("Picture captured and analyzed successfully!");
            console.log("Analysis Results:", data.analysis);

            // Display the results
            const results = data.analysis;
            const resultText = `
                  Age: ${results.age} \n
                  Gender: ${results.gender} \n
                  Race: ${JSON.stringify(results.race)} \n
                  Emotion: ${JSON.stringify(results.emotion)}
                `;
            alert(resultText);
            alert(data);
          }
        })
        .catch((error) => {
          console.error("Error capturing image:", error);
          alert("An error occurred while capturing the image.");
        });
    }

    return {
      handleFlagClick,
      shouldRender,
      returnHome,
      takePicture,
      language,
    };
  },
}).mount("#app");

// function stopVideoFeed() {
//   // Send POST request to stop the feed
//   fetch("/stop_feed", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   });
//   // Keep the src unchanged so the last frame remains visible
// }
// function handleFlagClick(lang) {
//   alert(lang);
// }

// function startVideoFeed() {
//   // Send POST request to start the feed
//   fetch("/start_feed", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   }).then(() => {
//     // Temporarily clear the video stream and reset the src
//     const videoStream = document.getElementById("video-stream");
//     videoStream.src = ""; // Clear the src temporarily
//     setTimeout(() => {
//       videoStream.src = "/video_feed"; // Reset src to start feed
//     }, 100); // Small delay to ensure feed is restarted
//   });
// }
