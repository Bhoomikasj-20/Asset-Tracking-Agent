import ApiService from "../services/apiService.js";

const assetList = document.getElementById("assetList");
const addAssetBtn = document.getElementById("addAssetBtn");
const modal = document.getElementById("assetModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const assetForm = document.getElementById("assetForm");
const modalTitle = document.getElementById("modalTitle");

let editAssetId = "";

document.addEventListener("DOMContentLoaded", () => {
  loadAssets();
});

async function loadAssets() {
  try {
    const assets = await ApiService.get("/assets/");
    renderAssets(assets);
  } catch (error) {
    console.error("Error fetching assets:", error);
    assetList.innerHTML = `<p class="error-text">Failed to load assets.</p>`;
  }
}

function renderAssets(assets = []) {
  if (!assets.length) {
    assetList.innerHTML = `<p>No assets found. Add a new one!</p>`;
    return;
  }

  assetList.innerHTML = assets
    .map(
      (a) => `
      <div class="asset-card">
        <div class="asset-info">
          <h3>${escapeHtml(a.asset_type)} (${escapeHtml(a.brand)})</h3>
          <p><strong>Model:</strong> ${escapeHtml(a.model_number)}</p>
          <p><strong>Assigned To:</strong> ${escapeHtml(a.assigned_to)}</p>
          <p><strong>Purchase Date:</strong> ${escapeHtml(a.purchase_date)}</p>
          <p><strong>Status:</strong> ${escapeHtml(a.status)}</p>
        </div>
        <div class="asset-actions">
          <button
            class="btn-edit"
            data-action="edit"
            data-id="${a.asset_id}"
            data-asset_type="${escapeAttr(a.asset_type)}"
            data-brand="${escapeAttr(a.brand)}"
            data-model_number="${escapeAttr(a.model_number)}"
            data-assigned_to="${escapeAttr(a.assigned_to)}"
            data-purchase_date="${escapeAttr(a.purchase_date)}"
            data-status="${escapeAttr(a.status)}"
          >
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn-delete" data-action="delete" data-id="${a.asset_id}">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </div>
    `
    )
    .join("");
}

addAssetBtn.addEventListener("click", () => openModal());
closeModalBtn.addEventListener("click", () => closeModal());

function openModal(asset = null) {
  modal.style.display = "flex";
  if (asset) {
    modalTitle.textContent = "Edit Asset";
    document.getElementById("asset_type").value = asset.asset_type;
    document.getElementById("brand").value = asset.brand;
    document.getElementById("model_number").value = asset.model_number;
    document.getElementById("assigned_to").value = asset.assigned_to;
    document.getElementById("purchase_date").value = asset.purchase_date;
    document.getElementById("status").value = asset.status;
  } else {
    modalTitle.textContent = "Add New Asset";
    assetForm.reset();
  }
}

function closeModal() {
  modal.style.display = "none";
  editAssetId = null;
}

assetForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const assetData = {
    asset_type: assetForm.asset_type.value,
    brand: assetForm.brand.value,
    model_number: assetForm.model_number.value,
    assigned_to: assetForm.assigned_to.value,
    purchase_date: assetForm.purchase_date.value,
    status: assetForm.status.value,
  };

  try {
    if (editAssetId) {
      await ApiService.put(`/assets/${editAssetId}`, assetData);
    } else {
      await ApiService.post("/assets/", assetData);
    }
    closeModal();
    loadAssets();
  } catch (error) {
    console.error("Error saving asset:", error);
  }
});

async function editAsset(id, data) {
  editAssetId = id;
  openModal(data);
}

async function deleteAsset(id) {
  try {
    await ApiService.delete(`/assets/${id}`);
    loadAssets();
  } catch (error) {
    console.error("Error deleting asset:", error);
  }
}

assetList.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = btn.dataset.id;

  if (action === "edit") {
    const data = {
      asset_type: btn.dataset.asset_type,
      brand: btn.dataset.brand,
      model_number: btn.dataset.model_number,
      assigned_to: btn.dataset.assigned_to,
      purchase_date: btn.dataset.purchase_date,
      status: btn.dataset.status,
    };
    editAsset(id, data);
  } else if (action === "delete") {
    deleteAsset(id);
  }
});

window.onclick = function (event) {
  if (event.target === modal) closeModal();
};

function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeAttr(str = "") {
  return String(str).replaceAll('"', "&quot;");
}
