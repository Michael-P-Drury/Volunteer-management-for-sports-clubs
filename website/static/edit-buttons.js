function editEmails() {
    var T = document.getElementById("profile-box-email"),
        displayValue = "";
    if (T.style.display == "")
        displayValue = "none";

    T.style.display = displayValue;
}

function editMobile() {
    var T = document.getElementById("profile-box-mobile"),
        displayValue = "";
    if (T.style.display =="")
        displayValue = "none";

    T.style.display = displayValue;
}