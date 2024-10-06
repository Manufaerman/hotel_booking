
var endpoint = '/api/chart/data/'
var defaultData = [];
var labels = [];
var rowData = []

$.ajax({
	method:"GET",
	url: endpoint,
	success: function(data){
		defaultData = data.uno
		labels = data.labels
		rowData = data.dos
		setChart();

		},
		error: function(error_data){
			console.log('error')
			console.log(error_data)
		}
})

function setChart(){
	const ctx = document.getElementById('myChart');
	const ctx2 = document.getElementById('myChart2');
	const ctx3 = document.getElementById('myChart3');
	const ctx4 = document.getElementById('myChart4');
    console.log(rowData);


	  	new Chart(ctx, {
			type: 'bar',
			data: {
		  		labels: labels,
		  	datasets: [{
				label: '2023 total',
				data: defaultData,
				borderWidth: 1
		  }]

		},
		options: {
		  scales: {
			y: {
			  beginAtZero: true
			}
		  }
		}
	  });

	new Chart(ctx2, {
			type: 'line',
			data: {
		  		labels: labels,
		  	datasets: [{
				label: '2023 total',
				data: defaultData,
				borderWidth: 1
		  }]

		},
		options: {
		  scales: {
			y: {
			  beginAtZero: true
			}
		  }
		}
	  });

		new Chart(ctx3, {
			type: 'line',
			data: {
		  		labels: labels,
		  	datasets: [
		{
      label: 'Dataset 1',
      data: defaultData,
      yAxisID: 'y',
    },
    {
      label: 'Dataset 2',
      data: rowData,
      yAxisID: 'y1',
    }
]

		},
		options: {
		  scales: {
			y: {
			  beginAtZero: true
			}
		  }
		}
	  });

new Chart(ctx4, {
			type: 'bar',
			data: {
		  		labels: labels,
		  	datasets: [
		{
      label: 'Dataset 1',
      data: defaultData,
      yAxisID: 'y',
    },
    {
      label: 'Dataset 2',
      data: rowData,
      yAxisID: 'y1',
    }
]

		},
		options: {
		  scales: {
			y: {
			  beginAtZero: true
			}
		  }
		}
	  });
}