const petNameInput = document.getElementById("petNameInput");
const createProfileBtn = document.getElementById("createProfileBtn");
const profileSelect = document.getElementById("profileSelect");
const historyLog = document.getElementById("historyLog");

async function loadProfiles() {
    const response = await fetch("/get-pets");
    const pets = await response.json();
    
    profileSelect.innerHTML = '<option value="">-- Choose a Pet --</option>';
    pets.forEach(pet => {
        const option = document.createElement("option");
        option.value = pet.id;
        option.textContent = pet.name;
        profileSelect.appendChild(option);
    });
}
loadProfiles();

createProfileBtn.addEventListener("click", async function() {
    const name = petNameInput.value.trim();
    if(!name) return alert("Please enter a pet name.");

    const formData = new FormData();
    formData.append("name", name);

    await fetch("/create-profile", {
        method: "POST",
        body: formData
    });

    petNameInput.value = "";
    alert("New pet profile saved!");
    loadProfiles();
});

profileSelect.addEventListener("change", async function() {
    const petId = this.value;
    if(!petId) {
        historyLog.innerHTML = "Select a pet from the list to look up their past medical logs.";
        return;
    }

    historyLog.innerHTML = "Fetching history records...";
    const response = await fetch(`/get-history/${petId}`);
    const records = await response.json();

    if(records.length === 0) {
        historyLog.innerHTML = "This pet has a clean record! No historical diagnoses found.";
        return;
    }

    historyLog.innerHTML = records.map(record => `
        <div style="border: 1px solid #ddd; padding: 12px; margin-bottom: 10px; border-radius: 6px; background-color: #f9f9f9;">
            <p><strong>Condition:</strong> ${record.disease}</p>
            <p><strong>First Aid:</strong> ${record.first_aid}</p>
            <p><strong>Vet Guidance:</strong> ${record.vet}</p>
            <p style="text-align: right; margin: 0;"><small style="color: #777;">Checked: ${record.timestamp || 'Just now'}</small></p>
        </div>
    `).join('');
});