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
