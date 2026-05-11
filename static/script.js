 const imageInput = document.getElementById("imageInput");
  const preview = document.getElementById("preview");
  const predictBtn = document.getElementById("predictBtn");
  const result = document.getElementById("result");

  imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
      };

      reader.readAsDataURL(file);
    }
  });

  predictBtn.addEventListener("click", async function () {

    if (imageInput.files.length == 0) {
      alert("Please upload an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);

    result.innerText = "Predicting...";

    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    result.innerText = "Prediction: " + data.prediction;
  });