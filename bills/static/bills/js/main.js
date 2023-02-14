const menuBill = document.querySelector('.figure');
const menuMobile = document.querySelector('.mobile-menu-link');
const billNav = document.querySelector('.bill-nav');
const paymentNav = document.querySelector('.payment-nav');
const providerNav = document.querySelector('.provider-nav');
const billMobileNav = document.querySelector('.bill-mob-nav');
const paymentMobileNav = document.querySelector('.payment-mob-nav');
const providerMobileNav = document.querySelector('.provider-mob-nav')
const place = document.querySelector('.place');
const body = document.querySelector('.bills');
const navBar = document.querySelector('.navbar');
const printButton = document.querySelector('.print-button');


const bottomMenu = document.querySelector('.hint');
const asideMenu = document.querySelector('.mobile-menu');


menuBill.addEventListener('click', toggleBottomMenu);
menuMobile.addEventListener('click', toggleAsideMenu);
window.addEventListener('load',toggleNavSelected);

printButton.addEventListener("click", function(){
    window.print();
});

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


function toggleNavSelected(){
    
    if (place.classList.contains('p-bills')){
        billNav.classList.add('navbar-selected');
        billMobileNav.classList.add('navbar-mobile-selected');
    }
    if (place.classList.contains('p-payments')){
        paymentNav.classList.add('navbar-selected');   
        paymentMobileNav.classList.add('navbar-mobile-selected');
    }
    if (place.classList.contains('p-providers')){
        providerNav.classList.add('navbar-selected');   
        providerMobileNav.classList.add('navbar-mobile-selected');
    }
    if (place.classList.contains('n-bill')){
        navBar.classList.add('inactive');
    }
}