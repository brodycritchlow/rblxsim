//index js
 const sleep = time => new Promise(res => setTimeout(res, time, "done sleeping"));

function calculateRapTotal() {
    var items = document.getElementsByClassName('card-text item-rap');
    var rapTotalElement = document.getElementById('rap-total');

    var rap_total = 0;
    for (var i = 0; i < items.length; ++i) {
        var item = items[i];  
        rap_total += parseInt(item.innerText.replaceAll("$", "").replaceAll(",",""))
    }
    rapTotalElement.innerHTML = "$" + rap_total.toLocaleString();
}

function check(res) {
    if (res.status == 200) {
        return "Successfully, sold!"
    } else {
        return "Failed to sell item."
    }
}
function sell(elem) {
    var item_name = elem.closest("div").querySelector(".item-name").innerText;
    bootbox.confirm(`Do you really want to sell, ${item_name}`,
        function(result) {
        if (result==true) {
            elem.closest("div").parentElement.remove();
            calculateRapTotal();
            fetch('/sell/' + encodeURIComponent(item_name), {
                method: 'POST',
            })
            .then(response => bootbox.alert(check(response)))
            .catch(error => console.error(error));
        }
    });
}

async function getItems() {
    fetch('/click/')
        .then((response) => response.json())
        .then((data) => {
            document.querySelector('#item1').innerText ="$" + Math.round(data.new).toLocaleString() + "";
        });
}
async function trade(elem) {
    var item_name = elem.closest("div").querySelector(".item-name").innerText
    var item_rap = elem.closest("div").querySelector(".item-rap").innerText.replaceAll("$", "").replaceAll(",", "");
    
    document.location = '/trade_offers/' + encodeURIComponent(item_name)
}
