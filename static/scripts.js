function updateElapsedTime(startTime) {
    const elapsedTimeElement = document.getElementById("elapsed-time-value");
    const currentTime = new Date();
    const elapsedTime = Math.floor((currentTime - startTime) / 1000);
    elapsedTimeElement.textContent = elapsedTime;
  }
  
  function adjustHeight(element, defaultHeight) {
    element.style.height = defaultHeight; // Reset element height in case of decreasing text lines
    element.style.height = `${element.scrollHeight}px`; // Set element height equal to scroll height
  }
  
  const dynamicHeightInputs = Array.from(document.getElementsByClassName("dynamic-height"));
  dynamicHeightInputs.forEach(input => {
    input.addEventListener('input', () => adjustHeight(input, '1em'));
    adjustHeight(input, '1em');
  });
  
  const generateBtn = document.getElementById("generate-btn");
  if (generateBtn) {
    generateBtn.addEventListener("click", async event => {
      event.preventDefault();
  
      const bodyInput = document.getElementById("body-input");
      const keywordsInput = document.getElementById("keywords-input");
      const newsOutput = document.getElementById("news-output");
      const loader = document.getElementById("loader");
      const elapsedTimeContainer = document.getElementById("elapsed-time-container");
  
      if (!bodyInput.value) {
        alert("Please enter a valid text before processing.");
        return;
      }
  
      loader.classList.remove("hidden");
      elapsedTimeContainer.classList.remove("hidden");
  
      const startTime = new Date();
      updateElapsedTime(startTime);
      const elapsedTimeInterval = setInterval(() => updateElapsedTime(startTime), 1000);
  
      const formData = new FormData();
      formData.append("body", bodyInput.value);
      formData.append("keywords", keywordsInput.value);
  
      try {
        const response = await fetch("/rephrase", { method: "POST", body: formData });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error ? data.error : "Network response was not ok");
        }
        loader.classList.add("hidden");
        clearInterval(elapsedTimeInterval);
        newsOutput.value = data.result;
      } catch (error) {
        console.error("Error:", error);
        loader.classList.add("hidden");
        elapsedTimeContainer.classList.add("hidden");
        clearInterval(elapsedTimeInterval);
      }
    });
  }