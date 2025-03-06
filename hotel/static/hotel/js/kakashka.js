console.log('hello world')

$.ajax({
    type: 'GET',
    url: '/pruebas-json/',
    success: function(response){
        console.log(response)
    },
    error: function(error){
        console.log(error)
    }
})