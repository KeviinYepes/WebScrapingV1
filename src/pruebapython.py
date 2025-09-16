def procesar_datos(correo, password, codigo, fecha_inicial, fecha_final):
    # Aquí pones la lógica que quieras hacer con los datos
    resultado = {
        "correo": correo,
        "password": password,
        "codigo": codigo,
        "fecha_inicial": fecha_inicial,
        "fecha_final": fecha_final,
        "mensaje": f"Datos procesados correctamente para {correo}"
    }
    return resultado