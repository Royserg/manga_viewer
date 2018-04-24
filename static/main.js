const suggestions = document.querySelector('#suggestions');
const inputField = document.querySelector('#inputField');
const minLength = 1;

// convert input title for matching manga alias
const convertTitle = (title) => title.toLowerCase().split(" ").join("-");

// detect interaction on input
const inputHandler = (e) => {
    let title = convertTitle(e.target.value);
    let val = e.target.value;

    if (title.length > 1) {
        // make AJAX call
        let datalistOptions = [];

        // https://stackoverflow.com/questions/35038857/setting-query-string-using-fetch-get-request
        let url = new URL(`http://127.0.0.1:5000/api/suggestions?query=${title}`)
        // let params = {query: title}
        // url.search = new URLSearchParams(params)

        // get 10 pick from db - AJAX call
        fetch(url)
        .then((res) => res.json())
        .catch(error => console.log('ERROR occured: ${error}'))
        .then((data) => {
            // clear the datalist options
            suggestions.innerHTML = "";
            let options = "";
            
            // save each result as an option to append to datalist
            for(let manga in data){
                // create new option node for each result
                let optionNode = document.createElement('option');
                // set value attribute of the option
                optionNode.setAttribute('value', manga);
                // add created option node to the datalist
                suggestions.appendChild(optionNode);
            }
            
            // https://stackoverflow.com/questions/30022728/perform-action-when-clicking-html5-datalist-option/32205204
            datalistOptions = suggestions.childNodes;
            for (let i = 0; i < datalistOptions.length; i++) {
                if (datalistOptions[i].value === val) {
                    // if typed or selected value matches one of the suggestions
                    window.open(`/${title}`, "_self");
                    break;
                }
            }
        });
    };
}
// attach inputHandler to input field
inputField.addEventListener('input', inputHandler);

// inputField.addEventListener('input', e => {
    // detect when user type and backspace characters
    // console.log(e);
    // console.log(e.target);
    // if (e.inputType === "insertText" || e.inputType === "deleteContentBackward"){
    //     // console.log(e);
    //     let q = convertTitle(e.target.value);
    //     if (q.length > 1){
    //         // https://stackoverflow.com/questions/35038857/setting-query-string-using-fetch-get-request
    //         let url = new URL('http://127.0.0.1:5000/api/suggestions')
    //         let params = {query: q}
    //         url.search = new URLSearchParams(params)

    //         // get 10 pick from db - AJAX call
    //         fetch(url)
    //         .then((res) => res.json())
    //         .then((data) => {
    //             // clear the datalist options
    //             suggestions.children = "";
    //             let options = "";
                
    //             // save each result as an option to append to datalist
    //             for(let manga in data){
    //                 options += `<option value="${manga}" >last chapter: ${data[manga]['last_date']}</option>`;
    //             }
    //             suggestions.innerHTML = options;
    //         })
    //     }
    // } else {
    //     console.log(e);
    //     // detect selecting option or pressing enter
    //     // let title = convertTitle(e.target.value);
    //     // // // go to the manga_alias url
    //     // window.open(`/${title}`, "_self");
    // }
// });

