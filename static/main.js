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
        // make AJAX call to api that returns 5 manga suggestions
        axios.get('/api/suggestions', {
            params: {
                query: title
            }
        })
            .then((res) => {
                // clear the datalist options
                suggestions.innerHTML = "";
                // save each result as an option to append to datalist
                for(let manga in res.data){
                    // create new option node for each result
                    let optionNode = document.createElement('option');
                    // set value attribute of the option
                    optionNode.setAttribute('value', manga);
                    // add created option node to the datalist
                    suggestions.appendChild(optionNode);
                }
            
                // https://stackoverflow.com/questions/30022728/perform-action-when-clicking-html5-datalist-option/32205204
                let datalistOptions = suggestions.childNodes;
                for (let i = 0; i < datalistOptions.length; i++) {
                    if (datalistOptions[i].value === val) {
                        // if typed or selected value matches one of the suggestions
                        window.open(`/manga/${title}`, "_self");
                        break;
                    }
                }
            })
            .catch((err) => console.log(err));        
    }
}

// attach event Listener to input field
inputField.addEventListener('input', inputHandler);
