//index js
 
const sleep = time => new Promise(res => setTimeout(res, time, "done sleeping"));

function check(res) {
    if (res.status == 200) {
        return "Successfully, sold!"
    } else {
        return "Failed to sell item."
    }
}
function sell(elem) {
    var item_name = elem.closest("div").parentNode.querySelector(".card-info").querySelector(".item-name").innerText;
    // bootbox.confirm(`Do you really want to sell, ${item_name}`,
    //     function(result) {
        
    // });
    elem.closest("div").parentElement.remove();
    
    fetch('/sell/' + encodeURIComponent(item_name), {
        method: 'POST',
    })
    .then(response => console.log(check(response)))
    .catch(error => console.error(error));

    sleep(3000)
    location.reload();
}

async function getItems() {
    fetch('/click/')
        .then((response) => response.json())
        .then((data) => {
            document.querySelector('#item1').innerText ="$" + Math.round(data.new).toLocaleString() + "";
        });
}
async function trade(elem) {
    var item_name = elem.closest("div").parentNode.querySelector(".card-info").querySelector(".item-name").innerText;
    var item_rap = elem.closest("div").parentNode.querySelector(".card-info").querySelector(".item-rap").innerText.replaceAll("$", "").replaceAll(",", "");
    
    document.location = '/trade_offers/' + encodeURIComponent(item_name)
}