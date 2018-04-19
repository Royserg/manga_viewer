const suggestions = document.querySelector('#suggestions');
const query = document.querySelector('#q');
const minLength = 1;


// convert input title for matching manga alias
const convertTitle = (title) => title = title.toLowerCase().split(" ").join("-");


query.addEventListener('input', e => {;
    // detect when user type and backspace characters
    if (e.inputType === "insertText" || e.inputType === "deleteContentBackward"){
        let q = convertTitle(e.target.value);
        if (q.length > 1){
            // https://stackoverflow.com/questions/35038857/setting-query-string-using-fetch-get-request
            let url = new URL('http://127.0.0.1:5000/api/suggestions')
            let params = {query: q}
            url.search = new URLSearchParams(params)

            // get 10 pick from db - AJAX call
            fetch(url)
            .then((res) => res.json())
            .then((data) => {
                // clear the datalist options
                suggestions.children = "";
                let options = "";
                
                // save each result as an option to append to datalist
                for(let manga in data){
                    options += `<option value="${manga}" >last chapter: ${data[manga]['last_date']}</option>`;
                }
                suggestions.innerHTML = options;
                
            })
        }
    } else {
        // detect selecting option or pressing enter
        let title = convertTitle(e.target.value);
        // form.action = `/${title}`;
        // form.submit()
        window.open(`/${title}`, "_self");
    }   
});


