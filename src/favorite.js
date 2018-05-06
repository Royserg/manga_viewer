// HTTP async requests https://github.com/axios/axios 
const axios = require('axios');

const favorite = document.getElementById('favorite');

const subscribe = () => {
    if (favorite.classList.contains('far')) {
        // When user subscribes
            // send axios request to subscribe and add to db
            
        // change icon
        favorite.classList.remove('far');
        favorite.classList.add('fas');
    } else {
        // When user unsubscribes
            // send axios request to unsubscribe and remove from db

        // change icon
        favorite.classList.remove('fas');
        favorite.classList.add('far');
    }
    
}

favorite.addEventListener('click', subscribe);