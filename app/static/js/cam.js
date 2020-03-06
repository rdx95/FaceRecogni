Webcam.set({
    width: 320,
    height: 240,
    image_format: 'jpeg',
    jpeg_quality: 90
});
Webcam.attach('#my_camera');

// <!-- Code to handle taking the snapshot and displaying it locally -->
function take_snapshot() {

    // take snapshot and get image data
    Webcam.snap(function (data_uri) {
        // display results in page
        document.getElementById('res_img').src = data_uri;
        var x = document.getElementById("results");
        if (x.style.display === "none") {
            x.style.display = "block";
        }

    });
}

document.getElementById("submit").addEventListener("click",function (e){
// function sub_data() {
    e.preventDefault();

    imgUrl = document.getElementById("res_img").src;
    // Split the base64 string in data and contentType
    var block = imgUrl.split(";");
    // Get the content type of the image
    var contentType = block[0].split(":")[1];
    // get the real base64 content of the file
    var realData = block[1].split(",")[1];

    // Convert it to a blob to upload
    var blob = b64toBlob(realData, contentType);
    // Create a FormData and append the file with "image" as parameter name
    var formDataToUpload = new FormData();

    formDataToUpload.append("image", blob, 'selfie.png');
    formDataToUpload.append("name", window.prompt('What is the name ?'));

    console.log(formDataToUpload.getAll('name'));


    console.log(formDataToUpload);

    $.ajax({
        type: "POST",
        enctype: 'multipart/form-data',
        url: "http://faces.t38.in/checklabel",

        data: formDataToUpload,
        processData: false,
        contentType: false,
        cache: false,
        timeout: 600000,
        success: function (data) {

            console.log(data);
            console.log("SUCCESS : ", data.message);
            // $("#res_msg").html(data.message);
            // $("#res_dis").html(data.distance);
            // $("#btnSubmit").prop("disabled", false);

        },
        error: function (e) {

            console.log(e.responseText);
            // $("#res_msg").html(e.responseText);
            console.log("ERROR : ", e);


        },
        complete: function () {
            console.log("Request Finished.");
        }
    });


});

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