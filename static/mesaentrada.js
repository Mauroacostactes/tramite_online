
// Función para ocultar los mensajes después de unos segundos
function hideMessages() {
    var messages = document.getElementsByClassName('message');
    for (var i = 0; i < messages.length; i++) {
        messages[i].style.display = 'none';
    }
}

// Ocultar automáticamente los mensajes después de 2.5 segundos
setTimeout(hideMessages, 2500);

// Inicializar DataTable para la tabla sin movimiento
        $('#tabla_sin_movimiento').DataTable({
            "scrollY": "400px", // Altura máxima de la tabla antes de habilitar el scroll vertical
            "scrollCollapse": true, // Hacer colapsar el espacio vacío si la tabla es más pequeña que la altura definida
            "paging": false, // Desactivar paginación
            "language": {
                "Show":"Mostrar",
                "search": "Buscar:",
                "lengthMenu": "Mostrar _MENU_ registros por página",
                "info": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
                "paginate": {
                    "previous": "Anterior",
                    "next": "Siguiente"
                }
            },
            "rowCallback": function(row, data) {
                var estado = data[7]; // Cambia el índice según la posición de la columna "estado" en tus datos
                if (estado == "Sin Novedad") {
                    $(row).addClass('sin-novedad');
                }
            }
        });
        // Inicializar DataTable para la tabla completados y rechazados
        $('#tabla_completados_rechazados').DataTable({
            "scrollY": "400px", // Altura máxima de la tabla antes de habilitar el scroll vertical
            "scrollCollapse": true, // Hacer colapsar el espacio vacío si la tabla es más pequeña que la altura definida
            "paging": false, // Desactivar paginación
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            "language": {
                "Show":"Mostrar",
                "search": "Buscar:",
                "lengthMenu": "Mostrar _MENU_ registros por página",
                "info": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
                "paginate": {
                    "previous": "Anterior",
                    "next": "Siguiente"
                }
            },
            "rowCallback": function(row, data) {
                var estado = data[7]; // Cambia el índice según la posición de la columna "estado" en tus datos
                if (estado == "Completo") {
                    $(row).addClass('completo');
                } else if (estado == "Rechazado") {
                    $(row).addClass('rechazado');
                }   
            }
        });

        // Función para mostrar la ventana modal con los datos del trámite
        function mostrarModal(id_solicitud, partida, municipio, tipoTramite, fechaCreacion, nombreApellido, dniCuitCuil) {
            // Rellenar los elementos de la ventana modal con los datos del trámite
            $('#modalId_solicitud').text(id_solicitud);
            $('#modalPartida').text(partida);
            $('#modalMunicipio').text(municipio);
            $('#modalTipoTramite').text(tipoTramite);
            $('#modalFechaCreacion').text(fechaCreacion);
            $('#modalNombreApellido').text(nombreApellido);
            $('#modalDniCuitCuil').text(dniCuitCuil);
            // Mostrar la ventana modal
            $('#detalleTramiteModal').modal('show');
        }

        // Evento clic en las filas de la tabla
        $(document).ready(function () {
        $('table tbody tr').click(function () {
            var id_solicitud = $(this).find('td:eq(0)').text();
            var partida = $(this).find('td:eq(1)').text();
            var municipio = $(this).find('td:eq(2)').text();
            var tipoTramite = $(this).find('td:eq(3)').text();
            var fechaCreacion = $(this).find('td:eq(4)').text();
            var nombreApellido = $(this).find('td:eq(5)').text();
            var dniCuitCuil = $(this).find('td:eq(6)').text();

            mostrarModal(id_solicitud, partida, municipio, tipoTramite, fechaCreacion, nombreApellido, dniCuitCuil);
            // Evento clic en el botón de descarga en la ventana modal
            
        });

        $('#guardarObservacionesBtn').click(function () {
             var id_solicitud = $('#modalId_solicitud').text();
             var observaciones = $('#observaciones').val();
             var estado = $('#estado').val();

                // Enviar el formulario al servidor (puedes usar AJAX)
                $.ajax({
                        type: 'POST',
                        url: '/guardar_observaciones',  // Ruta en tu servidor para manejar esta solicitud
                        data: { id_solicitud: id_solicitud, observaciones: observaciones, estado: estado },
                        success: function (response) {
                        
                            console.log(response);
                            $('#observaciones').val('');
                            $('#detalleTramiteModal').modal('hide'); // Cerrar la ventana modal
                        },
                        error: function (error) {
                        
                            console.error(error);
                        }
                    });
         });

        $('#descargarPdfBtn').click(function () {
            var id_solicitud = $('#modalId_solicitud').text();
            var partida = $('#modalPartida').text();
            var tipoTramite = $('#modalTipoTramite').text();
            var nombreApellido = $('#modalNombreApellido').text();

            var urlDescargaPdf = 'http://localhost:8000/tramites/' +id_solicitud+' '+ partida + ' ' + tipoTramite +' '+nombreApellido +'.pdf';

            // Redireccionar para iniciar la descarga
            window.open(urlDescargaPdf, '_blank');
            
        });

        
     });
