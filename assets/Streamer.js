let viewport;
let stream;
let ws;
let user_id;
let class_id;
let peer;
let user_name;
let board;
let drawing = false;

function Looper() {
  setInterval(snapImg, 2000);
}

function Send(cmd, attrib) {
  ws.send(
    JSON.stringify({
      id: user_id,
      token: getCookie("portal_token"),
      cmd: cmd,
      attrib: attrib,
    })
  );
}

function snapImg() {
  if (drawing == true) {
    var img = board[0].toDataURL("image/png");
    ws.send(
      JSON.stringify({
        id: user_id,
        token: getCookie("portal_token"),
        cmd: "img",
        attrib: class_id,
        attrib2: img,
      })
    );
    console.log(img);
  }
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

function showBoard() {
  Looper();
  drawing = true;
  document.getElementById("board").style.left = "0px";
  document.getElementById("show-board").style.filter = "invert()";
  document.getElementById("show-board").onclick = () => {
    hideBoard();
  };
  document.getElementById("show-board").src =
    "http://localhost:8000/static/close.png";
  Send("show_board", class_id);
}

function hideBoard() {
  drawing = false;
  document.getElementById("board").style.left = "-550px";
  document.getElementById("show-board").style.filter = "none";
  document.getElementById("show-board").onclick = () => {
    showBoard();
  };
  document.getElementById("show-board").src =
    "http://localhost:8000/static/board.png";
  Send("hide_board", class_id);
}

function Ask() {
  if (document.getElementById("question").value) {
    var question =
      user_name + " : " + document.getElementById("question").value;
    document.getElementById("question").value = null;
    ws.send(
      JSON.stringify({
        id: user_id,
        token: getCookie("portal_token"),
        cmd: "asked",
        attrib: class_id,
        attrib2: question,
      })
    );
  }
}

function fullLoaded() {
  board = document.getElementsByClassName("drawing-board-canvas");
  ws = new WebSocket("ws://localhost:8512");
  user_id = document.getElementById("user_id").value;
  class_id = document.getElementById("class_id").value;
  user_name = document.getElementById("user_name").value;
  ws.onopen = () => {
    console.log("Connected to websocket");
    // Send('start_class',JSON.stringify({id:class_id,peer_id:'dummy_id'}))
    peer = new Peer();
    peer.on("open", (peer_id) => {
      Send("start_class", JSON.stringify({ id: class_id, peer_id: peer_id }));
    });
  };
  var defaultBoard = new DrawingBoard.Board("board");
  l = document.getElementsByClassName("start-it");
  l[0].style.display = "block";

  ws.onmessage = (message) => {
    console.log(message);
    var data = JSON.parse(message.data);
    if (data[0] == "population") {
      document.getElementById("num-population").innerHTML = data[1];
    }
    if (data[0] == "question") {
      var para = document.createElement("P");
      para.innerText = data[1];
      para.className = "a-question";
      document
        .getElementById("questions")
        .insertBefore(para, document.getElementsByClassName("a-question")[0]);
    }
    if (data[0] == "peer_id") {
      console.log("Called");
      var call = peer.call(data[1], stream);
    }
  };
}

function startClass() {
  var curtain = document.getElementsByClassName("curtain");
  var button = document.getElementsByClassName("start-it");
  curtain[0].style.height = "0%";
  setTimeout(function () {
    curtain[0].style.display = "none";
    button[0].style.display = "none";
  }, 300);
  viewport = document.getElementById("viewport");
  navigator.getUserMedia(
    { video: { width: 1280, height: 720 }, audio: true },
    (stream_dat) => {
      stream = stream_dat;
      viewport.srcObject = stream;
      viewport.play();
    },
    (error) => {
      console.log(error);
    }
  );
}

function pauseStream() {
  document.getElementById("paused-message").style.display = "block";
  var pausePlayimg = document.getElementById("pausePlayimg");
  stream.getTracks()[0].enabled = false;
  stream.getTracks()[1].enabled = false;
  pausePlayimg.onclick = () => {
    resumeStream();
  };
  pausePlayimg.src = "http://localhost:8000/static/play.png";
  Send("pause", class_id);
}

function resumeStream() {
  document.getElementById("paused-message").style.display = "none";
  var pausePlayimg = document.getElementById("pausePlayimg");
  stream.getTracks()[0].enabled = true;
  stream.getTracks()[1].enabled = true;
  pausePlayimg.onclick = () => {
    pauseStream();
  };
  pausePlayimg.src = "http://localhost:8000/static/pause.png";
  Send("resume", class_id);
}
document.addEventListener("keydown", (event) => {
  const keyName = event.key;

  if (keyName === "Enter") {
    Ask();
  }
});
