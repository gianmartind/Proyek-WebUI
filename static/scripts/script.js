var model_set = false;
var image_path = "";

document.getElementById("image-input").onchange = function () {
  let value = this.value.split("\\");
  document.getElementById("image-input-button").innerHTML = value[2];
};

function remove_green(option) {
  option.classList.remove("w3-green");
}
function choose_model() {
  let model_name = document.getElementById("model").value;
  let model_loader = document.getElementById("model-loader");
  //temporary
  document.getElementById("conf_control").style.display = "none";
  document.getElementById("detect_result").style.display = "none";
  //
  model_loader.textContent = ".";
  fetch("/get_model?model_name=" + model_name)
    .then((response) => {
      return response.json();
    })
    .then((result) => {
      console.log(result.result);
      //image_path = result.result
      model_set = true;
      model_loader.textContent = "O";
      document.getElementById("selected-model").textContent = result.result;
      num_classes = model_name.split("_")[0]
      //temporary
      if(num_classes == 2) {
        document.getElementById("conf_control").style.display = "block";
        document.getElementById("detect_result").style.display = "block";
        document.getElementById("conf_sedan").style.display = "none";
        document.getElementById("name_sedan").style.display = "none";
        document.getElementById("detect-sedan").style.display = "none";
      } else if(num_classes == 3) {
        document.getElementById("conf_control").style.display = "block";
        document.getElementById("detect_result").style.display = "block";
        document.getElementById("conf_sedan").style.display = "block";
        document.getElementById("name_sedan").style.display = "inline";
        document.getElementById("detect-sedan").style.display = "inline";
      }
      //
      //console.log(image_path)
    });
}

function upload_file() {
  let input = document.querySelector('input[type="file"]');

  let data = new FormData();
  data.append("file", input.files[0]);
  data.append("user", "hubot");

  fetch("/upload", {
    method: "POST",
    body: data,
  })
    .then((response) => {
      return response.json();
    })
    .then((result) => {
      document.getElementById("input-img").src = result.result;
      image_path = result.result;
      console.log(image_path);
      document.getElementById("image-input-button").innerHTML = "Choose File";
      document.querySelector('input[type="file"]').value = "";
    });
}

var detection = document.getElementById("detection");
var detect_total = document.getElementById("detect-total");
var detect_mobil = document.getElementById("detect-mobil");
var detect_motor = document.getElementById("detect-motor");
var detect_sedan = document.getElementById("detect-sedan");
var loader = document.getElementById("loader-container");

function detect_image() {
  if (model_set & (image_path != "")) {
    loader.style.display = "block";
    let mobil_conf = document.getElementById("mobil_conf").value / 100;
    let motor_conf = document.getElementById("motor_conf").value / 100;
    let sedan_conf = document.getElementById("sedan_conf").value / 100;

    fetch("/detect?image_path=" + image_path + "&mobil_conf=" + mobil_conf + "&motor_conf=" + motor_conf + "&sedan_conf=" + sedan_conf)
      .then((response) => {
        return response.json();
      })
      .then((result) => {
        detection.src = result.path;
        detect_mobil.innerHTML = result.mobil;
        detect_motor.innerHTML = result.motor;
        detect_sedan.innerHTML = result.sedan;
        detect_total.innerHTML = result.mobil + result.motor;
        console.log(result);
        loader.style.display = "none";
        //image_path = result.result
        //console.log(image_path)
      });
  } else {
    alert("Model not set and/or Image not selected!");
  }
}

function sliderValue(x) {
    let label_id = x.id + "_val"
    let conf_val = x.value
    document.getElementById(label_id).textContent = conf_val / 100
}
