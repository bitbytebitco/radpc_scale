function generate_config(indexes, data_points, rlines, y_label, x_label, title){
    return config = {
        type: 'line',
        data: {
            //labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            labels: indexes,
            datasets: [{
                label: y_label,
                //backgroundColor: window.chartColors.red,
                backgroundColor: getRandomColorHex(),
                borderColor: getRandomColorHex(),
                data: data_points,
                fill: false,
            },
            {
                label: 'regression',
                backgroundColor: window.chartColors.red,
                //backgroundColor: getRandomColorHex(),
                borderColor: window.chartColors.orange,
                data: rlines,
                fill: false,
            }]
        },
        options: {
            elements: {
                    point:{
                        radius: 0
                    }
                },
            responsive: true,
            title: {
                display: true,
                text: title, 
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: x_label, 
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: y_label 
                    }
                }]
            }
        }
    };
    /**
   * function to generate random color in hex form
   */
  function getRandomColorHex() {
    var hex = "0123456789ABCDEF",
        color = "#";
    for (var i = 1; i <= 6; i++) {
      color += hex[Math.floor(Math.random() * 16)];
    }
    return color;
  }
}


