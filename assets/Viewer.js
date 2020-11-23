let viewport;
let stream;
let ws;
let user_id;
let class_id;
let peer;
let user_name;
let board;

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

function muteStream() {
  viewport.muted = true;
  var muteButton = document.getElementById("pausePlayimg");
  muteButton.src = "http://localhost:8000/static/mute.png";
  muteButton.onclick = () => {
    unmuteStream();
  };
}

function unmuteStream() {
  viewport.muted = false;
  var muteButton = document.getElementById("pausePlayimg");
  muteButton.src = "http://localhost:8000/static/unmute.png";
  muteButton.onclick = () => {
    muteStream();
  };
}

function showBoard() {
  document.getElementById("board").style.left = "0px";
}

function hideBoard() {
  document.getElementById("board").style.left = "-550px";
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

function playB() {
  viewport.play();
  document.getElementById("playBtn").style.display = "none";
}

function showPlayBtn(params) {
  document.getElementById("playBtn").style.display = "block";
}

function fullLoaded() {
  ws = new WebSocket("ws://localhost:8512");
  user_id = document.getElementById("user_id").value;
  class_id = document.getElementById("class_id").value;
  user_name = document.getElementById("user_name").value;
  viewport = document.getElementById("viewport");
  ws.onopen = () => {
    console.log("Connected to websocket");
    peer = new Peer();
    // ws.send(JSON.stringify({id:user_id,token:getCookie('portal_token'),cmd:'enter_class',attrib:class_id,attrib2:'dummy_peer'}))
    peer.on("open", (peer_id) => {
      ws.send(
        JSON.stringify({
          id: user_id,
          token: getCookie("portal_token"),
          cmd: "enter_class",
          attrib: class_id,
          attrib2: peer_id,
        })
      );
    });
    peer.on("call", function (call) {
      console.log("Call recieved");
      call.answer();
      call.on("stream", function (streamed) {
        console.log(streamed);
        stream = streamed;
        viewport.srcObject = streamed;
        viewport.play();
        // if (viewport !== undefined) {
        //         viewport.then(function() {
        //           console.log('Play Success');
        //         }).catch(function(error) {
        //           showPlayBtn();

        //         });}
      });
    });
    peer.on("error", (error) => {
      console.log(error);
    });

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

      if (data[0] == "img") {
        document.getElementById("image").src = data[1];
      }
      if (data[0] == "pause") {
        pauseStream();
      }
      if (data[0] == "resume") {
        resumeStream();
      }
      if (data[0] == "show_board") {
        showBoard();
      }
      if (data[0] == "hide_board") {
        hideBoard();
      }
    };
  };
}

function enterClass() {
  var curtain = document.getElementsByClassName("curtain");
  var button = document.getElementsByClassName("start-it");
  curtain[0].style.height = "0%";
  setTimeout(function () {
    curtain[0].style.display = "none";
    button[0].style.display = "none";
  }, 300);
  // viewport.play();
  // if (viewport !== undefined) {
  //     viewport.then(function() {
  //       // Automatic playback started!
  //     }).catch(function(error) {
  //       // Automatic playback failed.
  //       // Show a UI element to let the user manually start playback.

  //     });
  //   }
  // navigator.getUserMedia(
  //     {video:{ width: 1280, height: 720 },
  //         audio:true},
  //     (stream_dat)=>{
  //         stream = stream_dat;
  //         // viewport.srcObject=stream;
  //         // viewport.play();
  //     },
  //     (error)=>{
  //         console.log(error)
  //     }
  // )
}

function pauseStream() {
  document.getElementById("paused-message").style.display = "block";
  viewport.pause();
}

function resumeStream() {
  document.getElementById("paused-message").style.display = "none";
  viewport.play();
}

document.addEventListener("keydown", (event) => {
  const keyName = event.key;

  if (keyName === "Enter") {
    Ask();
  }
});
