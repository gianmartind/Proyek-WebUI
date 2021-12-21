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
  // document.getElementById("conf_control").style.display = "none";
  // document.getElementById("detect_result").style.display = "none";
  //
  model_loader.classList.remove("fa-exclamation", "fa-check", "fa-spinner");
  model_loader.classList.add("fa-spinner");
  fetch("/get_model?model_name=" + model_name)
    .then((response) => {
      return response.json();
    })
    .then((result) => {
      console.log(result.result);
      //image_path = result.result
      model_set = true;
      model_loader.classList.remove("fa-exclamation", "fa-check", "fa-spinner");
      model_loader.classList.add("fa-check");
      document.getElementById("selected-model").textContent = result.result;
      num_classes = model_name.split("_")[0]
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
var detect_bus = document.getElementById("detect-bus");
var detect_truk = document.getElementById("detect-truk");
var loader = document.getElementById("loader-container");
var result_graph = document.getElementById("result-graph");
var result_count;

function detect_image() {
  if (model_set & (image_path != "")) {
    loader.style.display = "block";
    let mobil_conf = document.getElementById("mobil_conf").value / 100;
    let motor_conf = document.getElementById("motor_conf").value / 100;
    let sedan_conf = document.getElementById("sedan_conf").value / 100;
    let bus_conf = document.getElementById("bus_conf").value / 100;
    let truk_conf = document.getElementById("truk_conf").value / 100;

    fetch("/detect?image_path=" + image_path + "&mobil_conf=" + mobil_conf + "&motor_conf=" + motor_conf + "&sedan_conf=" + sedan_conf + "&bus_conf=" + bus_conf + "&truk_conf=" + truk_conf)
      .then((response) => {
        return response.json();
      })
      .then((result) => {
        detection.src = result.path;
        detect_mobil.innerHTML = result.count.mobil;
        detect_motor.innerHTML = result.count.motor;
        detect_sedan.innerHTML = result.count.sedan;
        detect_bus.innerHTML = result.count.bus;
        detect_truk.innerHTML = result.count.truk;
        detect_total.innerHTML = result.count.mobil + result.count.motor + result.count.sedan + result.count.bus + result.count.truk;
        console.log(result.count);
        loader.style.display = "none";
        result_count = result.count
        let plot = create_plot(result_count);
        Plotly.newPlot('result-graph', plot.data, plot.layout, plot.config);
        //image_path = result.result
        //console.log(image_path)
      });
  } else {
    alert("Model not set and/or Image not selected!");
  }
}

function create_plot(count){
  var data = [
    {
      x: Object.keys(count),
      y: Object.values(count),
      type: 'bar'
    }
  ];

  var layout = {
    title: {
      text:'Object Count',
      font: {
        family: 'Google',
      },
      xref: 'paper',
      x: 0.0,
    },
    xaxis: { type: 'category' }
  };

  var config = {responsive: true}

  return {"data":data, "layout":layout, "config":config};
}

function sliderValue(x) {
    let label_id = x.id + "_val"
    let conf_val = x.value
    document.getElementById(label_id).textContent = conf_val / 100
}
