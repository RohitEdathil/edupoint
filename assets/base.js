let ws;
let user_id;
let token;

function notif_sound() {
  document.getElementById("notif-sound").play();
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function hideAlert() {
  console.log("called");
  var bar = document.getElementById("bar");
  var clo = document.getElementById("close-notif");
  clo.style.display = "none";
  bar.className = "notif-hidden";
  bar.innerHTML = " ";
}

function showAlert() {
  console.log("called");
  var bar = document.getElementById("bar");
  var clo = document.getElementById("close-notif");
  bar.className = "notif";
  clo.style.display = "block";
  bar.innerHTML = "You got a Notification";
  notif_sound();
}

function valueIndicator() {
  slider = document.getElementById("rating-slider");
  outBox = document.getElementById("value-box");
  outBox.innerHTML = "Rating:" + slider.value + "%";
}

function Logout() {
  ws.send(JSON.stringify({ id: user_id, token: token, cmd: "logout" }));
  window.location.href = "/logout";
}

function Main() {
  ws = new WebSocket("ws://localhost:8512");
  user_id = document.getElementById("user_id").value;
  if (user_id == "") {
    window.location.href = "/";
  }
  ws.onopen = () => {
    console.log("Connected to WebSocket");
    token = getCookie("portal_token");
    ws.send(JSON.stringify({ id: user_id, token: token }));
  };
  ws.onclose = () => {
    console.log("Disconnected");
  };

  ws.onmessage = (message) => {
    console.log(message.data);
    if (message.data == "alert") {
      showAlert();
    }
    if (message.data == "invalid") {
      window.location.href = "/";
      console.log("invalid");
    }
  };
}

function showit() {
  document.getElementById("cur_user_container").style.display = "flex";
  document.getElementById("name-container").style.display = "none";
}
document.onload = () => {
  document.getElementById("head").onclick = function () {
    document.getElementById("cur_user_container").style.display = "none";
    document.getElementById("name-container").style.display = "flex";
  };
};
