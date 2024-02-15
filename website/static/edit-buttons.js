function editEmails() {
    var T = document.getElementById("profile-box-text"),
        displayValue = "";
    if (T.style.display == "")
        displayValue = "none";

    T.style.display = displayValue;
}