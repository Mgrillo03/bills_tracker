const menuBill = document.querySelector('.figure');
const menuMobile = document.querySelector('.mobile-menu-link');

const bottomMenu = document.querySelector('.hint');
const asideMenu = document.querySelector('.mobile-menu');

menuBill.addEventListener('click', toggleBottomMenu);
menuMobile.addEventListener('click', toggleAsideMenu);

function toggleBottomMenu(){   
    const isAsideMenuOpen = !asideMenu.classList.contains('inactive');
    
    if (isAsideMenuOpen) {
        asideMenu.classList.add('inactive');
    } 

    bottomMenu.classList.toggle('inactive');    
}

function toggleAsideMenu(){
    const isBottomMenuOpen = !bottomMenu.classList.contains('inactive');

    if (isBottomMenuOpen) {
        bottomMenu.classList.add('inactive');
    } 
    asideMenu.classList.toggle('inactive');
}