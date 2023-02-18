const cheackboxSearchOverdue = document.querySelector('.checkbox-overdue');
const cheackboxSearchUnpaid = document.querySelector('.checkbox-unpaid');
const searchButton = document.querySelector('.search-button');
const orderByMenuButton = document.querySelector('.search-right-menu');


const orderByMenu = document.querySelector('.order-by-menu');

cheackboxSearchOverdue.addEventListener('click',activateSearchButton);
cheackboxSearchUnpaid.addEventListener('click',activateSearchButton);
// orderByMenuButton.addEventListener('click', toggleOrderByMenu);



function activateSearchButton(){
    searchButton.click();
 }
