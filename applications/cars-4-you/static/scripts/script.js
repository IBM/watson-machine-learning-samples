var logoImage = document.getElementById("logoimg")
var textInput = document.getElementById('user-text');
var userComment = document.getElementById("user-comment");
var sadFaceImage = document.getElementById('sad');
var happyFaceImage = document.getElementById('happy');
var responseFace = document.getElementById("response-face");
var sendButton = document.getElementById("send-button");
var feedbackComment = document.getElementById("feedback-comment");
var questionBox = document.getElementById("question");
var responseBox = document.getElementById("response");
var sidebar = document.getElementById("sidebar");
var modelSidebar = document.getElementById("sidebar-models");
var errorPanel = document.getElementById("error-message");
var saveButton = document.getElementById("sidebar-save");
var cancelButton = document.getElementById("sidebar-cancel");
var saveModelButton = document.getElementById("sidebar-model-save");
var cancelModelButton = document.getElementById("sidebar-model-cancel");
var customerName = document.getElementById("cust-name");
var firstName = document.getElementById("first-name-input");
var secondName = document.getElementById("last-name-input");
var genderInput = document.getElementById("gender-input");
var ageInput = document.getElementById("age-input");
var statusInput = document.getElementById("status-input");
var childrenInput = document.getElementById("children-input");
var carownerInput = document.getElementById("owner-input");
var activeInput = document.getElementById("active-input");
var areaActionSelection = document.getElementById("area-input");
var sentimentSelection = document.getElementById("nlu-input");
var happyFacePath = "staticImages/thumb_up.svg";
var happyFaceSelectedPath = "staticImages/thumb_up_on.svg";
var sadFacePath = "staticImages/thumb_down.svg";
var sadFaceSelectedPath = "staticImages/thumb_down_on.svg";

var payloadData = {
    "comment": "",
    "gender": "Male",
    "status": "S",
    "childrens": 2,
    "age": 36,
    "customer": "Active",
    "owner": "Yes",
    "satisfaction": -1
};

var userData = {
    "username": "John",
    "lastname" : "Smith",
    "payload": payloadData
};

cancelButton.onclick = function () {
    reset_sidebar();
    show_hide_sidebar();
}

saveButton.onclick = function () {
    update_customer_name();
    show_hide_sidebar();
}

cancelModelButton.onclick = function(){
    show_hide_model_sidebar();
}

saveModelButton.onclick = function() {
    show_hide_model_sidebar();
    update_models();
}

sadFaceImage.addEventListener('click', select_sad);
happyFaceImage.addEventListener('click', select_happy);

document.getElementById("avatar-button").addEventListener('click', show_hide_sidebar);
document.getElementById("user-welcome").addEventListener('click', show_hide_sidebar);
document.getElementById("logout-button").addEventListener('click', function() { location.reload(); });

document.getElementById("model-button").addEventListener('click', show_hide_model_sidebar);

check_deployments();

logoImage.onclick = function () {
    location.reload();
}

sendButton.onclick = function () {
    var comment = textInput.value;
    userComment.innerHTML = comment;

    if (userData.payload.satisfaction === -1) {
        send_with_satisfaction(comment);
    }
    else {
        send_request(comment);
    }
}

function send_with_satisfaction(text) {
    $.ajax({
        method: "POST",
        contentType: "text/html; charset=utf-8",
        url: "/analyze/satisfaction",
        data: text,
        success: function (data) {
            if (data === '0') {
                userData.payload.satisfaction = 0;
                send_request(text);
            }
            else if(data === '1') {
                userData.payload.satisfaction = 1;
                send_request(text);
            }
            else{
                userData.payload.satisfaction = 1;
                send_request(text);
            }
        },
        error: function (data, textStatus) {
            if (textStatus === "timeout"){
                print_error("Unable to score Satisfaction AI function. Reason: request timeout");
            }
            else{
                print_error(data['responseText']);
            }                
        },
        timeout: 30000,
        dataType: "json"
    });
}

function get_area_action_deployments() {
    $.get(
        "/functions/area",
        function (data) {
            var currentValue = areaActionSelection.value;
            areaActionSelection.innerHTML = "";
            if (data['deployments'].length == 0){
                var opt = document.createElement('option');
                opt.value = "< no deployments >";
                opt.innerHTML = "< no deployments >";
                areaActionSelection.appendChild(opt);
            }
            else{
                data['deployments'].forEach(element => {
                    var opt = document.createElement('option');
                    opt.value = element['guid'];
                    opt.innerHTML = element['name'];
                    areaActionSelection.appendChild(opt);
                }); 
                if (currentValue != null && currentValue != ""){
                    areaActionSelection.value = currentValue;
                }
            }
        }
    );
}

function get_satisfaction_deployments() {
    $.get(
        "/functions/satisfaction",
        function (data) {
            var currentValue = sentimentSelection.value;
            
            sentimentSelection.innerHTML = "";
            if (data['deployments'].length == 0){
                var opt = document.createElement('option');
                opt.value = "< no deployments >";
                opt.innerHTML = "< no deployments >";
                sentimentSelection.appendChild(opt);
            }
            else{
                data['deployments'].forEach(element => {
                    var opt = document.createElement('option');
                    opt.value = element['guid'];
                    opt.innerHTML = element['name'];
                    sentimentSelection.appendChild(opt);
                }); 
                if (currentValue != null && currentValue != ""){
                    sentimentSelection.value = currentValue;
                }
            }
        }
    );
}


function check_deployments(){
    get_satisfaction_deployments();
    get_area_action_deployments();

    $.get(
        "/checkdeployments",
        function (data) {
            if (data){
                sendButton.disabled = false;
            }
            else{
                sendButton.disabled = true;
                sendButton.title = "There is no deployments available."
            }
        }
    );
}

function send_request(comment) {
    userData.payload.comment = comment;

    $.ajax({
        method: "POST",
        contentType: "application/json",
        url: "/analyze/area",
        data: JSON.stringify(userData.payload),
        success: function (data) {

            update_face(userData.payload.satisfaction);
            feedbackComment.innerHTML = data['client_response'];

            questionBox.style.display = "none";
            responseBox.style.display = "block";
        },
        error: function (data) {
            print_error(data['responseText']);
        },
        dataType: "json"
    });
}

function update_models() {
    var models_payload = {"areaaction" : areaActionSelection.value, "satisfaction" : sentimentSelection.value }
    
    $.ajax({
        method: "POST",
        contentType: "application/json",
        url: "/functions",
        data: JSON.stringify(models_payload),

        error: function (data, textStatus, errorThrown) {
            print_error(errorThrown);
        },
        dataType: "json"
    });

}

function update_face(satisfaction) {
    if (satisfaction == 1) {
        responseFace.src = happyFaceSelectedPath;
    }
    else {
        responseFace.src = sadFaceSelectedPath;
    }
}

function select_happy() {
    happyFaceImage.src = happyFaceSelectedPath;
    sadFaceImage.src = sadFacePath;
    userData.payload.satisfaction = 1;
    sendButton.disabled = false;
}

function select_sad() {
    happyFaceImage.src = happyFacePath;
    sadFaceImage.src = sadFaceSelectedPath;
    userData.payload.satisfaction = 0;
    sendButton.disabled = false;
}

function deselect_faces() {
    happyFaceImage.src = happyFacePath;
    sadFaceImage.src = sadFacePath;
    sendButton.disabled = true;
}

function print_error(text) {
    errorPanel.innerHTML = String(text);
    errorPanel.style.display = "block";
}

function show_hide_sidebar() {
    if(modelSidebar.style.display === "block"){
        show_hide_model_sidebar();
    }
    if (sidebar.style.display === "none") {
        customerName.innerHTML = userData.username + " " + userData.lastname;
        sidebar.style.display = "block";
    }
    else {
        sidebar.style.display = "none"
    }
}

function show_hide_model_sidebar() {
    if(sidebar.style.display === "block"){
        show_hide_sidebar();
    }
    if (modelSidebar.style.display === "none") {
        check_deployments();
        modelSidebar.style.display = "block";
    }
    else {
        modelSidebar.style.display = "none"
    }
}

function update_customer_name() {
    userData.username = firstName.value;
    userData.lastname = secondName.value;
    userData.payload.gender = genderInput.value;
    userData.payload.age = ageInput.value;
    userData.payload.status = statusInput.value;
    userData.payload.childrens = childrenInput.value;
    userData.payload.customer = activeInput.value;
    userData.payload.owner = carownerInput.value;

    document.getElementById("user-welcome").value = "Welcome, " + firstName.value + "!";
}

function reset_sidebar() {
    firstName.value = userData.username;
    secondName.value = userData.lastname;
    genderInput.value = userData.payload.gender;
    ageInput.value = userData.payload.age;
    statusInput.value = userData.payload.status;
    childrenInput.value = userData.payload.childrens;
    activeInput.value = userData.payload.customer;
    carownerInput.value = userData.payload.owner;

    // console.log(userData);
}


/* DISABLE NLU */
var timeout = null;
textInput.onkeyup = function () {
    clearTimeout(timeout);
    timeout = setTimeout(get_sentiment, 800);
};
function get_sentiment() {
    var text = textInput.value;

    if (text.length > 10) {
        $.ajax({
            method: "POST",
            contentType: "text/html; charset=utf-8",
            url: "/analyze/satisfaction",
            data: text,
            success: function (data) {
                console.log(data)
                if (data == '0') {
                    select_sad();
                    userData.payload.satisfaction = 0;
                }
                else if(data == '1') {
                    select_happy();
                    userData.payload.satisfaction = 1;
                }
                else{
                    select_happy();
                    userData.payload.satisfaction = 1;
                }
            },
            error: function (data, textStatus) {
                if (textStatus === "timeout"){
                    print_error("Unable to score Satisfaction AI function. Reason: request timeout");
                }
                else{
                    print_error(data['responseText']);
                }                
            },
            timeout: 30000,
            dataType: "json"
        });
    }
    else {
        deselect_faces();
    }
}