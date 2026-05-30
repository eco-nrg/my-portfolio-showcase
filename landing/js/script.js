var menuResize = function() {
  if (this.innerWidth <= 991) {
    const menu = document.querySelector('#navbarSupportedContent .list-phone');
    menu?.classList.remove('list-phone');
    menu?.classList.add('navbar-nav');
  } else {
    const menu = document.querySelector('#navbarSupportedContent .navbar-nav');
    menu?.classList.remove('navbar-nav');
    menu?.classList.add('list-phone');
  }
}
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    [].forEach.call(document.querySelectorAll('img[data-src]'), function (img) {
      img.setAttribute('src', img.getAttribute('data-src'));
      img.onload = function () {
        img.removeAttribute('data-src');
      };
    });    
  }, 500);

  window.addEventListener('resize', menuResize);
  menuResize();
})
