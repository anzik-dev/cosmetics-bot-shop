/* Set the width of the side navigation to 300px */
function openNav() {
  document.getElementById("navbar").style.width = "200px";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
  document.getElementById("navbar").style.width = "0";
}



  function myFunction(imgs) {
    var MainImg = document.getElementById("MainImg");
    var smallimg = document.getElementById("small-img");
    MainImg.src = imgs.src;
  }
  