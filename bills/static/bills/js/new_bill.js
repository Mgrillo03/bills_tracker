const place = document.querySelector('.place');
const body = document.querySelector('.bills');
const navBar = document.querySelector('.navbar');
const billNav = document.querySelector('.bill-nav');
const paymentNav = document.querySelector('.payment-nav');
const providerNav = document.querySelector('.provider-nav');

window.addEventListener('load',toggleNavSelected);

function toggleNavSelected(){
    console.log('hola');

    if (place.classList.contains('p-bills')){
        billNav.classList.add('navbar-selected');
    }
    if (place.classList.contains('p-payments')){
        paymentNav.classList.add('navbar-selected');   
    }
    if (place.classList.contains('p-providers')){
        providerNav.classList.add('navbar-selected');   
    }
    if (place.classList.contains('n-bill')){
        navBar.classList.add('inactive');
    }
}

function numericFilter(txb) {
    txb.value = txb.value.replace(/[^\0-9]/ig, "");
 }