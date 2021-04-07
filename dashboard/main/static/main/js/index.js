window.addEventListener('beforeunload', function(event) {
    document.querySelector(
        "#loader").style.display = "block";
    document.querySelector(
        "#sub-content").style.visibility = "hidden";
});
window.onload = function(event) {
    document.querySelector(
        "#loader").style.display = "none";
    document.querySelector(
        "#sub-content").style.visibility = "visible";
};


function toggleSearch() {
	let camIcon = document.getElementById('search-cam');
    let textIcon = document.getElementById('search-text');
    let camInput = document.getElementById('upload-form');
    let textInput = document.getElementById('main-search');
    if (window.getComputedStyle(camIcon).display === "none") {
        camIcon.style.display = "block";
        textIcon.style.display = "none";
        textInput.style.display = "flex";
        camInput.value = "";
        camInput.style.display = "none";
    }
    else {
        camIcon.style.display = "none";
        textIcon.style.display = "block";
        textInput.style.display = "none";
        camInput.style.display = "block";
    }
}

function updateFilename(elId, targetId) {
    let fileElement = document.getElementById(elId);
    document.getElementById(targetId).innerHTML = fileElement.value.split(
        /(\\|\/)/g).pop();
}

function performSearch() {
    let camInput = document.getElementById('choose-file');
    let textInput = document.getElementById('main-search');
    let uploadForm = document.getElementById('upload-form');
    let searchForm = document.getElementById('search-form');
    console.log(camInput.value);
    if (camInput.value != undefined && camInput.value != null && camInput.value != "") {
        uploadForm.action = window.location.pathname;
        uploadForm.submit();
    } else {
        searchForm.submit();
    }
}

function performUpload() {
    let uploadForm = document.getElementById('deepfake-form');
    uploadForm.submit();
}

function blacklist() {
    var source = event.target || event.srcElement;
    let blacklistForm = source.parentNode.getElementsByClassName(
        'blacklist-form')[0];
    blacklistForm.submit();
}

function removeVideo() {
    var source = event.target || event.srcElement;
    let blacklistForm = source.parentNode.getElementsByClassName(
        'remove-view-form')[0];
    blacklistForm.submit();
}

function showAddModal() {
    let addForm = document.getElementById('add-form');
    let addModal = document.getElementById('add-criminal-modal');
    let backdrop = document.getElementById('backdrop');
    addModal.style.display = "block";
    backdrop.style.display = "block";
    addForm.reset();
}

function cancelAdd() {
    let addForm = document.getElementById('add-form');
    let addModal = document.getElementById('add-criminal-modal');
    let backdrop = document.getElementById('backdrop');
    addForm.reset();
    addModal.style.display = "none";
    backdrop.style.display = "none";

}

function addCamera() {
    let cameraViewContainer = document.getElementById('camera-view-container');
    let cameraForm = document.getElementById('camera-form');
    let clnCameraForm = cameraForm.cloneNode(true);
    clnCameraForm.style.display = 'block';
    cameraViewContainer.appendChild(clnCameraForm);
}
