const menuBill = document.querySelector('.add');

const aside = document.querySelector('.hint');

menuBill.addEventListener('hover', toggleDesktopMenu);

function toggleDesktopMenu(){   
    const isAsideOpen = !aside.classList.contains('inactive');

    if (isAsideOpen) {
        aside.classList.add('inactive');
    } 
    desktopMenu.classList.toggle('inactive');    
}
