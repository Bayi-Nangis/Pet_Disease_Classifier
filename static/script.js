const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const predictBtn = document.getElementById("predictBtn");
const result = document.getElementById("result");
const recommendation = document.getElementById("recommendation");
const firstAid = document.getElementById("first_aid");
const vet = document.getElementById("vet");

const petSelect = document.getElementById("petSelect");

async function populateDropdown() {
  const response = await fetch("/get-pets");
  const pets = await response.json();
  pets.forEach(pet => {
    const option = document.createElement("option");
    option.value = pet.id;
    option.textContent = pet.name;
    petSelect.appendChild(option);
  });
}
populateDropdown();

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
  formData.append("pet_id", petSelect.value);

  result.innerText = "Predicting...";

  const response = await fetch("/predict", {
    method: "POST",
    body: formData
  });
  const data = await response.json();

  result.innerText = "Prediction: " + data.prediction;
  recommendation.innerText = "Recommendation: " + data.recommended_action;
  firstAid.innerText = "First Aid: " + data.first_aid;
  vet.innerText = "When to see the vet: " + data.vet;
});