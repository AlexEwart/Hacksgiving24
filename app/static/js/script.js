import {
  createApp,
  ref,
} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
let lastMessage = "";

createApp({
  delimiters: ["[[", "]]"], // Custom delimiters
  setup() {
    const shouldRender = ref(true); // Use ref to make it reactive
    const language = ref("en");
    const title = ref("Loading...");
    const body = ref("Loading...");

    async function handleFlagClick(lang) {
      language.value = lang;
      shouldRender.value = false; // Update the value using `.value`

      // Wait for takePicture to complete
      await takePicture();

      let req_string = "/gpt_prompt";
      req_string += "?lang=" + lang;
      // change this to be changed per-terminal
      req_string += "&title=" + "Build It!";

      fetch(req_string, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          let objectthing = JSON.parse(data);

          // console.log(objectthing.youngest_age);
          // console.log(objectthing.info_title);
          console.log(objectthing.body);

          title.value = objectthing.title;
          body.value = objectthing.body;
        });
    }

    async function takePicture() {
      // Send POST request to capture image and await its completion
      await fetch("/capture_image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      console.log("took picture");
    }

    function returnHome() {
      title.value = "Loading...";
      body.value = "Loading...";
      shouldRender.value = true;
    }

    function startRecording() {
      fetch("/start_recording", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            alert("Failed to start audio recording: " + data.error);
          } else {
            console.log("Audio recording started");
          }
        })
        .catch((error) => {
          console.error("Error starting audio recording:", error);
          alert("An error occurred while starting audio recording.");
        });
    }

    function stopRecording() {
      fetch("/stop_recording", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
          } else {
            console.log("Audio recording stopped and saved");
            let objectthing = JSON.parse(data);

            // console.log(objectthing.youngest_age);
            // console.log(objectthing.info_title);
            console.log(objectthing.body);

            // TODO: updating gui doesnt work for some reason...
            body.value = objectthing.body;
          }
        })
        .catch((error) => {
          console.error("Error stopping audio recording:", error);
          alert("An error occurred while stopping audio recording.");
        });
    }

    return {
      handleFlagClick,
      shouldRender,
      returnHome,
      takePicture,
      language,
      title,
      startRecording,
      stopRecording,
      body,
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
