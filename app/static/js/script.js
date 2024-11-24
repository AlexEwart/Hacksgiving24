import {
  createApp,
  ref,
} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";

let lastMessage = "";
let lastStartRecordingTime = 0; // Timestamp to track last startRecording call
let recordingTimeout = null; // Timeout ID to handle returnHome after 30 seconds

createApp({
  delimiters: ["[[", "]]"], // Custom delimiters
  setup() {
    const shouldRender = ref(true); // Use ref to make it reactive
    const language = ref("en");
    const title = ref("Loading...");
    const body = ref("Loading...");
    const isSlideshowActive = ref(true); // Track slideshow state

    function toggleSlideshow(active) {
      const slideshowElement = document.getElementById("background-slideshow");
      if (slideshowElement) {
        if (active) {
          slideshowElement.style.animation = ""; // Resume animation
          slideshowElement.style.opacity = "1"; // Make it visible again
        } else {
          slideshowElement.style.animation = "none"; // Stop animation
          slideshowElement.style.opacity = "0.5"; // Dim it for a clear UI
        }
      }
    }

    async function handleFlagClick(lang) {
      language.value = lang;
      shouldRender.value = false; // Update the value using `.value`
      toggleSlideshow(false); // Stop the slideshow

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
      fetch("/return", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      title.value = "Loading...";
      body.value = "Loading...";
      shouldRender.value = true;
      toggleSlideshow(true); // Resume the slideshow
    }

    function toggleMute() {
      fetch("/toggle", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
    }

    function startRecording() {
      lastStartRecordingTime = Date.now(); // Update timestamp when startRecording is called

      // Clear any existing timeout to prevent duplicate calls to returnHome
      if (recordingTimeout) clearTimeout(recordingTimeout);

      // Set a timeout to call returnHome after 30 seconds
      recordingTimeout = setTimeout(() => {
        console.log("30 seconds elapsed, returning home.");
        returnHome();
      }, 30000);

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
      const wasRecentlyStarted = Date.now() - lastStartRecordingTime >= 500;

      // Clear the timeout as the recording is being stopped
      if (recordingTimeout) clearTimeout(recordingTimeout);

      fetch("/stop_recording", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ recentlyStarted: !wasRecentlyStarted }), // Pass false if called within 0.5 seconds
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
          } else {
            console.log("Audio recording stopped and saved");
            let objectthing = JSON.parse(data);

            console.log(objectthing.body);

            // Update the UI with the response body
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
      toggleMute,
      title,
      startRecording,
      stopRecording,
      body,
    };
  },
}).mount("#app");
