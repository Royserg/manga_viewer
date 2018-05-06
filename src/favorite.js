// HTTP async requests https://github.com/axios/axios 
const axios = require('axios');

const favorite = document.getElementById('favorite');

const subscribe = () => {
    let mangaID = favorite.getAttribute('data-manga-id');
    if (favorite.classList.contains('far')) {
        // When user subscribes
            // send axios request to subscribe and add to db
            axios.post('/api/subscribe', {
                manga_id: mangaID
            })
            .then((res) => console.log(res))
            .catch((err) => console.log(err));

        // change icon
        favorite.classList.remove('far');
        favorite.classList.add('fas');
    } else {
        // When user unsubscribes
            // send axios request to unsubscribe and remove from db
            axios.post('/api/unsubscribe', {
                manga_id: mangaID
            })
            .then((res) => console.log(res))
            .catch((err) => console.log(err));
        // change icon
        favorite.classList.remove('fas');
        favorite.classList.add('far');
    }
}

favorite.addEventListener('click', subscribe);