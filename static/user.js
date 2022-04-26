function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }
  
function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

document.addEventListener('DOMContentLoaded', function () {
    var id = getCookie('id');
    if (id == '') {
        var today = new Date();
        var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
        var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds() + today.getMilliseconds();
        var dateTime = date+' '+time;
        id = dateTime + Math.random()
    }
    setCookie("id", id, 365) // Update cookie to keep it stored
    document.querySelector("#id").value = id;

    // Process forms
    var form = document.getElementById('input-form');
    if (form.attachEvent) {
      form.attachEvent("submit", processForm);
    } else {
      form.addEventListener("submit", processForm);
    }

    if (navigator.userAgent.match(/Android/i) //I copied this if statement from https://redstapler.co/detect-mobile-device-with-javascript/
    || navigator.userAgent.match(/webOS/i) //This if statment is true if the website is being run in a mobile browser
    || navigator.userAgent.match(/iPhone/i)
    || navigator.userAgent.match(/iPad/i)
    || navigator.userAgent.match(/iPod/i)
    || navigator.userAgent.match(/BlackBerry/i)
    || navigator.userAgent.match(/Windows Phone/i)) {

    
  } else {
    document.getElementById('context').focus();
  }
});

function processForm(e) {
  if (e.preventDefault) e.preventDefault();

  /* do what you want with the form */
  var context = document.getElementById("context").value;
  var id = document.getElementById("id").value;
  // Disable form
  document.getElementById("context").disabled = true;
  document.getElementById("submit").disabled = true;
  // Get data
  postData('/query', {'context': context, 'id': id})
  .then(data => {
    if ("error" in data) {
      set_output("<div class='error'>" + data.error + "</div>")
    } else if ("result" in data) {
      set_output("<div class='result'>" + data.result + "</div>")
    }
    // Enable form
    document.getElementById("context").disabled = false;
    document.getElementById("submit").disabled = false;
    document.getElementById("context").value = '';
    document.getElementById("context").focus();
  });

  // You must return false to prevent the default form behavior
  return false;
}

function set_output(output) {
  document.getElementById('output').innerHTML = output;
}

// Example POST method implementation:
async function postData(url = '', data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}