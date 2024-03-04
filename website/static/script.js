document.getElementById("defaultOpen").click();

var slideIndex = 0;
showSlides();

function showSlides() {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    
    for (i = 0; i < slides.length; i++) {
        /*slides[i].style.display = 'none';*/
        slides[i].style.opacity = 0;
    }
    slideIndex++;

    if (slideIndex > slides.length) {
        slideIndex = 1}

    /*slides[slideIndex-1].style.display = 'block';*/
    slides[slideIndex-1].style.opacity = 1;
    setTimeout(showSlides, 3000);
}

function expand(button) {
    button.classList.toggle("active");
    var content = button.nextElementSibling;
    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
}

function showTab (tab, element) {
	const colour = '#468FAF';
  
  //Removes all content divs initially
	tabContent = document.getElementsByClassName("profile-tab-content");
  for (i = 0; i < tabContent.length; i++) {
    tabContent[i].style.display = "none";
  }
  
  //Removes colour from other tabs so that only one shows
  profileTabs = document.getElementsByClassName("profile-tab");
  for (i = 0; i < profileTabs.length; i++) {
    profileTabs[i].style.backgroundColor = "";
  }
  
  document.getElementById(tab).style.display = "block";
  element.style.backgroundColor = colour;
}

function showEdits () {

  var divs = document.getElementsByClassName("toggleEdit");

  for (var i = 0; i < divs.length; i++) {
    if (divs[i].style.display === "none") {
        divs[i].style.display = "block";
    } else {
        divs[i].style.display = "none";
    }
  }
}

