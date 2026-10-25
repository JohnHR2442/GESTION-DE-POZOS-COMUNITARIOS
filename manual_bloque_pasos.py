S = "/app/manual_pasos/"


def paso_img(n, texto, arch, titulo, alto=10.0):
    num = fig_n[0] + 1
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    par.paragraph_format.keep_with_next = True
    par.paragraph_format.space_after = Pt(4)
    rr = par.add_run(f"Paso {n}.  "); rr.bold = True; rr.font.color.rgb = RGBColor.from_string(AZUL)
    par.add_run(texto.replace("{f}", f"Figura {num}"))
    figuras([(arch, titulo)], alto)


def pasos_img(lista):
    for i, (t, a, c) in enumerate(lista, 1):
        paso_img(i, t, a, c)


# ======================= 3. INSTALACIÓN =======================
H1("3. Instalación")
p("La aplicación se distribuye a través de la tienda oficial Google Play con el nombre “Gestión de Pozos "
  "Comunitarios”. Para instalarla realice lo siguiente:")
pasos_img([
    ("Abra la aplicación Google Play Store, toque la barra de búsqueda y escriba “Gestión de Pozos Comunitarios”. "
     "La aplicación aparecerá en primer lugar de los resultados, publicada por Gestión Agrícola Escolar, como se "
     "observa en la {f}.", "/app/play_381cc52b1b7f2e86.png", "Búsqueda de la aplicación en Google Play."),
    ("Toque la aplicación para abrir su ficha, donde se muestran el tamaño, la clasificación “Apto para todo "
     "público” y las capturas de pantalla. Presione el botón Instalar ({f}).",
     "/app/play_40182583520d070b.png", "Ficha de la aplicación en Google Play."),
    ("Espere a que termine la descarga; el avance se muestra en porcentaje debajo del nombre de la aplicación "
     "({f}).", "/app/play_a98b372ce1eac741.png", "Descarga e instalación de la aplicación."),
    ("Cuando aparezca la etiqueta “Instalado”, presione Abrir para iniciar la aplicación ({f}). También puede "
     "abrirla desde el ícono que se agrega en la pantalla de su teléfono.",
     "/app/play_85d6d6591112f00c.png", "Aplicación instalada y lista para abrirse."),
])

# ======================= 4. PERFILES =======================
H1("4. Perfiles de usuario")
p("La aplicación cuenta con tres formas de acceso; cada una muestra únicamente las funciones que le "
  "corresponden, como se describe en la Tabla 2:")
tabla(["Perfil", "¿Necesita cuenta?", "Funciones principales"],
      [("Usuario en general", "No", "Ver la lista de socios del pozo, quién está en turno, horas de sobra y llamar a un socio."),
       ("Socio", "Sí", "Consultar su turno y calendario, reportar emergencias, ver notificaciones, multas, estadísticas, historial y registrar agua de sobra."),
       ("Contador", "Sí", "Registrar, editar, cobrar y eliminar multas; registrar recorridos (días sin servicio) del pozo.")],
      [3.5, 3, 8], "Perfiles de usuario de la aplicación.")

# ======================= 5. ACCESO =======================
H1("5. Acceso a la aplicación")
H2("5.1 Pantalla de inicio y selección de pozo")
p("Al abrir la aplicación se muestra la pantalla de bienvenida “Turnos de Pozo”. Cada pozo se identifica con "
  "un color que se mantendrá en todas las pantallas.")
FIG_PUBLICO = fig_n[0] + 3
pasos_img([
    ("Toque el nombre de su pozo (San Isidro, Zapata o Cárdenas); quedará marcado con una palomita, como se "
     "muestra en la {f}.", S + "a1_seleccion.png", "Selección del pozo en la pantalla de inicio."),
    ("Si es socio o contador, presione Iniciar sesión; se abrirá la pantalla de acceso de la {f}.",
     S + "a2_login.png", "Pantalla de inicio de sesión."),
    ("Si solo desea consultar quién tiene el turno, presione Soy usuario (ver turnos); se mostrará la consulta "
     "pública de la {f}.", S + "a3_publico.png", "Consulta pública de socios y turno actual."),
])
H2("5.2 Consulta pública de turnos")
p(f"En la consulta pública (Figura {FIG_PUBLICO}) los socios aparecen en su orden de rotación. El socio que "
  "tiene el turno del día aparece resaltado con la etiqueta “En turno” y los demás como “Inactivo”. Si algún "
  "socio registró horas de agua de sobra, se indica debajo de su nombre. En esta pantalla también puede:")
vineta(" llama directamente al socio.", "Botón de teléfono:")
vineta(" actualiza la información (también puede deslizar la lista hacia abajo).", "Ícono de flechas:")
vineta(" activa o desactiva los avisos del pozo.", "Ícono de campana:")

H2("5.3 Inicio de sesión")
FIG_INICIO = fig_n[0] + 3
pasos_img([
    ("Escriba el correo electrónico que le asignó el Comisariado ({f}).", S + "b1_correo.png",
     "Captura del correo electrónico."),
    ("Escriba su contraseña. Puede tocar el ícono del ojo para comprobar que esté bien escrita ({f}).",
     S + "b2_password.png", "Captura de la contraseña."),
    ("Presione Entrar. La aplicación lo llevará a la pantalla principal de su perfil ({f}).",
     S + "b3_inicio.png", "Pantalla de Inicio del socio."),
])
nota("La sesión permanece abierta en su teléfono; no necesita escribir su contraseña cada vez que abra la aplicación.")

H2("5.4 Recuperar contraseña")
p("Si olvidó su contraseña, presione “Se me olvidó la contraseña” en la pantalla de inicio de sesión. La barra "
  "superior indica la etapa en la que se encuentra:")
pasos_img([
    ("Escriba el correo de su cuenta y presione Siguiente; el código de seguridad se envía al Comisariado ({f}).",
     S + "c1_correo.png", "Solicitud del código de recuperación."),
    ("Solicite el código de 6 dígitos al Comisariado, escríbalo y presione Entrar. El código vence en 15 minutos "
     "({f}).", S + "c2_codigo.png", "Captura del código de seguridad."),
    ("Escriba su nueva contraseña (mínimo 6 caracteres), confírmela y presione Guardar contraseña ({f}).",
     S + "c3_nueva.png", "Captura de la nueva contraseña."),
    ("Se mostrará el mensaje de confirmación; presione Ir a iniciar sesión e ingrese con su nueva contraseña "
     "({f}).", S + "c4_listo.png", "Contraseña actualizada correctamente."),
])

# ======================= 6. SOCIO =======================
salto()
H1("6. Módulo del Socio")
p("Al iniciar sesión como socio se muestra una barra inferior con cuatro secciones: Inicio, Estadísticas, "
  "Historial y Perfil. Desde la pantalla de Inicio también se accede a Emergencia, Notificaciones, Multas y "
  "Agua de sobra.")
H2("6.1 Pantalla de Inicio: turno del día y calendario")
p(f"La pantalla de Inicio (Figura {FIG_INICIO}) muestra la tarjeta “Turno de hoy” con el nombre del socio al que "
  "le corresponde el agua, cuatro botones de acceso rápido y el calendario del mes, en el que se distinguen los "
  "colores descritos en la Tabla 3:")
tabla(["Color en el calendario", "Significado"],
      [("Color del pozo", "Días en los que usted tiene turno."),
       ("Verde", "Turno caído: día sin servicio registrado por el contador."),
       ("Rojo", "Emergencia o día festivo: no hay servicio y la rotación se recorre.")],
      [5, 9.5], "Significado de los colores del calendario.")
H2("6.2 Reportar una emergencia")
pasos_img([
    ("En la pantalla de Inicio presione el botón Emergencia y seleccione el tipo de problema: Fuga en tubería, "
     "Problema en hidrante o Baja presión de agua ({f}).", S + "d2_emergencia.png", "Selección del tipo de emergencia."),
    ("El aviso se envía de inmediato a todos los integrantes del pozo y aparece un mensaje de confirmación en la "
     "parte superior ({f}).", S + "d3_emergencia_ok.png", "Confirmación de emergencia reportada."),
])
H2("6.3 Notificaciones")
pasos_img([
    ("Presione el botón Notificaciones o el ícono de campana para ver los avisos del pozo con su fecha y hora "
     "({f}).", S + "d4_notificaciones.png", "Ventana de notificaciones."),
    ("Presione “Marcar todas como leídas” para limpiar los avisos nuevos ({f}).", S + "d5_leidas.png",
     "Notificaciones marcadas como leídas."),
])
H2("6.4 Consultar multas del pozo")
pasos_img([
    ("En la pantalla de Inicio presione Multas; se mostrará la lista de socios con el número de multas de cada "
     "uno ({f}).", S + "d6_multas.png", "Lista de multas por socio."),
    ("Toque el nombre de un socio para desplegar sus multas con el motivo, el monto y el estado Pagado o No "
     "pagado ({f}).", S + "d7_multas_socio.png", "Multas desplegadas de un socio."),
    ("Toque una multa para abrir su detalle con la descripción, el monto y la fecha ({f}).",
     S + "d8_multa_detalle.png", "Detalle de una multa."),
])
nota("Las multas solo pueden ser registradas y marcadas como pagadas por el contador. El pago se realiza "
     "directamente con el Comisariado.")
H2("6.5 Registrar agua de sobra")
pasos_img([
    ("En la pantalla de Inicio presione Agua de sobra, toque la lista “Selecciona las horas” y elija el número "
     "de horas que no utilizará ({f}).", S + "d9_horas.png", "Selección de horas de sobra."),
    ("Confirme presionando Seguro, o presione Cancelar para regresar ({f}).", S + "d10_seguro.png",
     "Confirmación de horas de sobra."),
    ("Aparecerá el mensaje Listo; presione OK. Las horas se mostrarán en la consulta pública y se notificará al "
     "pozo ({f}).", S + "d11_listo.png", "Horas de sobra registradas."),
    ("Para retirar horas que ya no tiene disponibles, use la lista “Quitar horas de sobra”, elija las horas y "
     "confirme ({f}).", S + "d12_quitar.png", "Retiro de horas de sobra."),
])
H2("6.6 Estadísticas")
pasos_img([
    ("Toque Estadísticas en la barra inferior para consultar los turnos del año, sus multas, el monto pendiente "
     "y pagado, la gráfica de multas pagadas y no pagadas y los socios con más multas ({f}).",
     S + "d13_estadisticas.png", "Pantalla de estadísticas."),
])
H2("6.7 Historial de turnos y exportación a PDF")
pasos_img([
    ("Toque Historial en la barra inferior y presione el selector de mes para elegir el periodo ({f}).",
     S + "d14_meses.png", "Selección del mes del historial."),
    ("Revise la lista de días con su estado (Turno asignado, Festivo o Sin servicio) y presione Exportar a PDF "
     "para guardar, imprimir o compartir sus turnos ({f}).", S + "d15_historial.png", "Historial mensual de turnos."),
])
H2("6.8 Perfil")
pasos_img([
    ("Toque Perfil en la barra inferior para ver su nombre, correo y tipo de usuario ({f}).", S + "d16_perfil.png",
     "Pantalla de perfil."),
    ("Active el interruptor Modo oscuro para cambiar los colores de la aplicación a tonos oscuros ({f}).",
     S + "d17_oscuro.png", "Perfil con modo oscuro activado."),
    ("Para cambiar su contraseña, escriba la actual y la nueva (mínimo 6 caracteres) y presione Actualizar "
     "contraseña ({f}).", S + "d18_cambiar_pass.png", "Cambio de contraseña."),
    ("Presione Cerrar sesión para salir; la aplicación regresará a la pantalla de inicio ({f}).",
     S + "d19_logout.png", "Pantalla de inicio después de cerrar sesión."),
])

# ======================= 7. CONTADOR =======================
salto()
H1("7. Módulo del Contador")
p("El contador de cada pozo dispone de tres secciones en la barra inferior: Multas, Recorrido y Perfil. "
  "La sección Perfil funciona igual que la del socio (apartado 6.8).")
H2("7.1 Registrar una multa")
pasos_img([
    ("Al iniciar sesión se muestra la lista de multas del pozo con el socio, el monto, la fecha y el estado "
     "({f}).", S + "e1_multas.png", "Lista de multas del pozo (contador)."),
    ("Presione el botón Nueva multa, ubicado en la esquina inferior derecha; se abrirá el formulario ({f}).",
     S + "e2_form.png", "Formulario de nueva multa."),
    ("Toque el campo Socio y seleccione al socio sancionado de la lista ({f}).", S + "e3_socios.png",
     "Selección del socio."),
    ("Escriba la Descripción o motivo de la multa ({f}).", S + "e4_descripcion.png", "Captura de la descripción."),
    ("Escriba el Monto en pesos y verifique la Fecha (AAAA-MM-DD), que por defecto es la del día ({f}).",
     S + "e5_monto.png", "Captura del monto y la fecha."),
    ("Presione Crear multa. La multa se agrega a la lista y el socio recibe una notificación ({f}).",
     S + "e6_creada.png", "Multa registrada en la lista."),
])
H2("7.2 Marcar como pagada, editar o eliminar una multa")
pasos_img([
    ("Toque una multa para desplegar su descripción y los botones de acción ({f}).", S + "e7_detalle.png",
     "Multa desplegada con sus acciones."),
    ("Presione Marcar pagada para registrar el pago; el estado cambia a Pagado y se guarda la fecha de pago "
     "({f}).", S + "e8_pagada.png", "Registro del pago de una multa."),
    ("Presione Editar para corregir el socio, la descripción o el monto y después presione Guardar cambios "
     "({f}).", S + "e9_editar.png", "Edición de una multa."),
    ("Presione el ícono de bote de basura para eliminar la multa y confirme con “Sí, eliminar” ({f}).",
     S + "e10_eliminar.png", "Confirmación para eliminar una multa."),
])
nota("Elimine una multa solo cuando haya sido registrada por error. Si la multa ya se cubrió, utilice "
     "“Marcar pagada” para conservar el registro como evidencia.", titulo="Importante:", color="FDE2E1")
H2("7.3 Registrar un recorrido (día sin servicio)")
p("Cuando un día no habrá servicio de agua, el contador lo registra para que la rotación se recorra "
  "automáticamente y ningún socio pierda su turno:")
pasos_img([
    ("Toque Recorrido en la barra inferior para ver el calendario del mes ({f}).", S + "e11_recorrido.png",
     "Calendario de recorridos."),
    ("Toque el día sin servicio y elija el motivo: Turno caído o Emergencia ({f}).", S + "e12_motivo.png",
     "Selección del motivo del recorrido."),
    ("Si eligió Emergencia, escriba la razón en el cuadro de texto ({f}).", S + "e13_razon.png",
     "Captura de la razón de la emergencia."),
    ("Presione Confirmar. El día se pinta en el calendario y se notifica a los socios ({f}).",
     S + "e14_confirmado.png", "Recorrido registrado."),
    ("Para deshacerlo, toque de nuevo el día marcado y presione Quitar recorrido ({f}).", S + "e15_quitar.png",
     "Quitar un recorrido registrado."),
])

