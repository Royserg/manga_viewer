const mangaBtn = document.querySelector('#mangaBtn');
const mangaList = document.querySelector('#mangaList');

// mangaBtn.addEventListener('click', getMangas);

// function getMangas(){
//     fetch('https://www.mangaeden.com/api/list/0/?p=0')
//     .then((res) => res.json())
//     .then((data) => {
//         data.manga.forEach(element => {
//             // title
//             mangaList.innerHTML += `<li>${element.t}
//             <img src="https://cdn.mangaeden.com/mangasimg/${element.im}" width=40 height=40 />
//             </li>
//             `
//         });
//     })
// }

//  580fb776719a161b4ecb1ecd  Vector Ball
// {
//     "a": "vector-ball", 
//     "c": [
//       "Action", 
//       "Comedy", 
//       "Drama", 
//       "School Life", 
//       "Shounen", 
//       "Supernatural"
//     ], 
//     "h": 7306, 
//     "i": "580fb776719a161b4ecb1ecd", 
//     "im": "6d/6da1578a4d7e573aea5e07fea360aa40522a86195643d831d56cca29.png", 
//     "ld": 1497481239.0, 
//     "s": 1, 
//     "t": "Vector Ball"
//   }, 
