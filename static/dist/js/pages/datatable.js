$(document).ready(function () {
    $('#example').DataTable({
        //Idioma español
        "language": {
            "emptyTable": "No hay datos disponibles en la tabla",
            "info": "Mostrando resgistrod del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Mostrando resgistrod del 0 al 0 de un total de 0 registros",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "lengthMenu": "Mostrar _MENU_ registros",
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "search": "Buscar:",
            "zeroRecords": "No se encontraron resultados",
            "paginate": {
                "first": "Primero",
                "last": "Ultimo",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "aria": {
                "sortAscending": ": activar para ordenar la columna ascendente",
                "sortDescending": ": activar para ordenar la columna descendente"
            }
        }
    });
});