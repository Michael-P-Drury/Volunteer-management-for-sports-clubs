// Initialise the slide index for the slideshow.
var slideIndex = 0;

// Function to manage to the slideshow
function showSlides() {
    var i;
    var slides = document.getElementsByClassName("mySlides");

    //Set all slides to be invisible initially.
    for (i = 0; i < slides.length; i++) {
        slides[i].style.opacity = 0;
    }
    
    //Reset index to loop back through to the final slide if the end is reached.
    if (slideIndex >= slides.length) {
        slideIndex = 0}
    
    //Makes the current side visible.
    slides[slideIndex].style.opacity = 1;
    slideIndex++;
    
    //Change the slides being shown every 3 seconds.
    setTimeout(showSlides, 3000);
    return 'Slideshow is running'
}

//Function to expand or collapse an item.
function expand(button) {
    button.classList.toggle("active");
    var content = button.nextElementSibling;
    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
}

//A function which is used to switch between tabs when in a tabbed interface.
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
  
  document.getElementById(tab).style.display = "flex";
  element.style.backgroundColor = colour;
}

//Function to toggle the visibility of editing elements on the page.
function showEdits (event) {

  event.preventDefault();

  var divs = document.getElementsByClassName("toggleEdit");

  for (var i = 0; i < divs.length; i++) {
    
    if (divs[i].style.display === "none" || divs[i].style.display === "") {
        divs[i].style.display = "block";
    } else {
        divs[i].style.display = "none";
    }
    
  }
}

//Function to ensure the correct input of time of the event management functions.
function checkTime() {
  var startTimeInput = document.querySelector('.admin-new-job-stime');
  var endTimeInput = document.querySelector('.admin-new-job-etime');

  // Update the end time input's min attribute whenever the start time changes
  startTimeInput.addEventListener('change', function() {
      endTimeInput.setAttribute('min', startTimeInput.value);
      endTimeInput.setCustomValidity(''); // Clear custom validity to prevent double messages
  });

  // Check the end time when the end time input changes
  endTimeInput.addEventListener('change', function() {
      if (startTimeInput.value && endTimeInput.value < startTimeInput.value) {
          // If invalid, set a custom validity message
          endTimeInput.setCustomValidity('End time cannot be before start time.');
      } else {
          // If valid, clear any custom validity messages
          endTimeInput.setCustomValidity('');
      }
      // This will trigger the browser's default handling of the custom validity message
      endTimeInput.reportValidity();
  });
}

//Function to toggle the visibility of elements for any removal actions.
function showRemoveButtons() {

  var divs = document.getElementsByClassName("remove-hidden");

  for (var i = 0; i < divs.length; i++) {
    if (divs[i].style.display === "none" || divs[i].style.display === "") {
        divs[i].style.display = "block";
    } else {
        divs[i].style.display = "none";
    }
  }

}

document.addEventListener('DOMContentLoaded', checkTime);