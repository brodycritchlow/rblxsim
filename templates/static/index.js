//index js
 
const sleep = time => new Promise(res => setTimeout(res, time, "done sleeping"));

function check(res) {
    if (res.status == 200) {
        return "Successfully, sold!"
    } else {
        return "Failed to sell item."
    }
}
function sell() {
    const selectedItems = document.querySelectorAll(".selected");
    const itemNames = Array.from(selectedItems).map(item => item.querySelector(".item-name").innerText);
    
    fetch('/sell', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({item_names: itemNames})
    })
    .then(response => console.log(check(response)))
    .catch(error => console.error(error));
    
    selectedItems.forEach(item => item.parentElement.remove());

    setTimeout(() => {
        location.reload();
    }, 3000);
}

async function getItems() {
    fetch('/click/')
        .then((response) => response.json())
        .then((data) => {
            document.querySelector('#item1').innerText ="$" + Math.round(data.new).toLocaleString() + "";
        });
}
async function trade() {
    const selectedItems = document.querySelectorAll(".selected");
    const itemNames = Array.from(selectedItems).map(item => item.querySelector(".item-name").innerText);

    if (itemNames.length === 1) {
        document.location = '/trade_offers/' + encodeURIComponent(itemNames[0]);
    } else if (itemNames.length > 1) {
        fetch('/trade_offers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({item_names: itemNames})
        })
        .then(response => console.log(check(response)))
        .catch(error => console.error(error));
        
        selectedItems.forEach(item => item.parentElement.remove());

        setTimeout(() => {
            location.reload();
        }, 3000);
    }
}


function select(elem) {
    if (elem.classList.contains("selected")) { elem.classList.remove("selected")}
    else if (document.getElementsByClassName("selected").length > 3) { return }
    else { elem.classList.add("selected") }
}