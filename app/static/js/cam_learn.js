var video = document.querySelector('#camera-stream'),
    image = document.querySelector('#snap'),
    start_camera = document.querySelector('#start-camera'),
    controls = document.querySelector('.controls'),
    delete_photo_btn = document.querySelector('#delete-photo'),
    upload_photo_btn = document.querySelector('#upload-to-learn'),
    download_photo_btn = document.querySelector('#download-photo'),
    error_message = document.querySelector('#error-message'),
    take_photo_btn = document.querySelector('#take-photo');

// The getUserMedia interface is used for handling camera input.
// Some browsers need a prefix so here we're covering all the options
navigator.getMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia);

if (!navigator.getMedia) {
    displayErrorMessage("Your browser doesn't have support for the navigator.getUserMedia interface.");
} else {

    // Request the camera.
    navigator.getMedia(
        // options
        {
            video: true,
            audio: false
        },
        // Success Callback
        function (stream) {
            // Create an object URL for the video stream and
            // set it as src of our HTML video element.
            // video.src = window.URL.createObjectURL(stream); // deprecated
            video.srcObject = stream;

            // Play the video element to start the stream.
            video.play();
            video.onplay = function () {
                showVideo();
            };

        },
        // Error Callback
        function (err) {
            displayErrorMessage("There was an error with accessing the camera stream: " + err.name, err);
        }
    );

}



// Mobile browsers cannot play video without user input,
// so here we're using a button to start it manually.
start_camera.addEventListener("click", function (e) {

    e.preventDefault();

    // Start video playback manually.
    video.play();
    showVideo();

});


take_photo_btn.addEventListener("click", function (e) {

    e.preventDefault();

    var snap = takeSnapshot();
    var i = document.getElementById("take-in");
    i.style.display = "block"

    // Show image. 
    image.setAttribute('src', snap);
    image.classList.add("visible");

    // Enable delete and save buttons
    delete_photo_btn.classList.remove("disabled");
    upload_photo_btn.classList.remove("disabled");
    download_photo_btn.classList.remove("disabled");

    // Set the href attribute of the download button to the snap url.
    download_photo_btn.href = snap;

    // Pause video playback of stream.
    video.pause();

});


delete_photo_btn.addEventListener("click", function (e) {


    e.preventDefault();

    var y = document.getElementById("take-in");
    y.style.display = "none";
    var x = document.getElementById("op");
    x.style.display = "none";
    // Hide image.
    image.setAttribute('src', "");
    image.classList.remove("visible");

    // Disable delete and save buttons
    delete_photo_btn.classList.add("disabled");
    upload_photo_btn.classList.add("disabled");
    download_photo_btn.classList.add("disabled");

    // Resume playback of stream.
    video.play();

});


upload_photo_btn.addEventListener("click", function (e) {


    e.preventDefault();

    var y = document.getElementById("take-in");
    y.style.display = "none";
    var x = document.getElementById("op");

    x.style.display = "block";
    $("#res_msg").html(" ");
    $("#res_dis").html(" ");
    imgUrl = image.getAttribute('src');
    // Split the base64 string in data and contentType
    var block = imgUrl.split(";");
    // Get the content type of the image
    var contentType = block[0].split(":")[1];
    // get the real base64 content of the file
    var realData = block[1].split(",")[1];

    // Convert it to a blob to upload
    var blob = b64toBlob(realData, contentType);

    //fetch data from form
    var name_data = document.getElementById("name").value;
    var app_name = document.getElementById("app-data").value;

    // Create a FormData and append the file with "image" as parameter name
    var formDataToUpload = new FormData();
    formDataToUpload.append("image", blob, 'selfie.png');
    formDataToUpload.append("name", name_data);
    formDataToUpload.append("app", app);
    // formDataToUpload.append("name", window.prompt('What is the name ?'));

    console.log(formDataToUpload.getAll('name'));


    console.log(formDataToUpload);

    $.ajax({
        type: "POST",
        enctype: 'multipart/form-data',
        url: "https://faces.t38.in/learn",

        data: formDataToUpload,
        processData: false,
        contentType: false,
        cache: false,
        timeout: 600000,
        success: function (data) {

            console.log(data);
            console.log("SUCCESS : ", data.message);
            $("#res_msg").html(data.message);
            $("#res_dis").html(data.distance);
            // $("#btnSubmit").prop("disabled", false);

        },
        error: function (e) {

            console.log(e.responseText);
            $("#res_msg").html(e.responseText);
            console.log("ERROR : ", e);


        },
        complete: function () {
            console.log("Request Finished.");
        }
    });

});


function showVideo() {
    // Display the video stream and the controls.

    hideUI();
    video.classList.add("visible");
    controls.classList.add("visible");
}


function takeSnapshot() {
    // Here we're using a trick that involves a hidden canvas element.  

    var hidden_canvas = document.getElementById('canvas');
    var context = hidden_canvas.getContext('2d');

    var width = video.videoWidth;
    var height = video.videoHeight;

    if (width && height) {

        // Setup a canvas with the same dimensions as the video.
        hidden_canvas.width = width;
        hidden_canvas.height = height;


        // Make a copy of the current frame in the video on the canvas.
        context.drawImage(video, 0, 0, width, height);

        // Turn the canvas image into a dataURL that can be used as a src for our photo.
        return hidden_canvas.toDataURL("image/png", 1.0);
    }
}


function displayErrorMessage(error_msg, error) {
    error = error || "";
    if (error) {
        console.log(error);
    }

    error_message.innerText = error_msg;

    hideUI();
    error_message.classList.add("visible");
}


function hideUI() {
    // Helper function for clearing the app UI.

    controls.classList.remove("visible");
    start_camera.classList.remove("visible");
    video.classList.remove("visible");
    snap.classList.remove("visible");
    error_message.classList.remove("visible");
}


/**
 * Convert a base64 string in a Blob according to the data and contentType.
 * 
 * @param b64Data {String} Pure base64 string without contentType
 * @param contentType {String} the content type of the file i.e (image/jpeg - image/png - text/plain)
 * @param sliceSize {Int} SliceSize to process the byteCharacters
 * @see http://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript
 * @return Blob
 */
function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {
        type: contentType
    });
    return blob;
}