import datetime
import json
import os

FORMATO_FECHA = "%d/%m/%Y"
FECHA_ACTUAL = datetime.date.today()
TURNOS = {"M": "Mañana", "T": "Tarde", "N": "Noche"}

ARCH_CLIENTES = "clientes.json"
ARCH_PLATILLOS = "platillos.json"
ARCH_PEDIDOS = "pedidos.json"

clientes = {}
platillos = {}
pedidos = {}

contador_folio = 1001

menu = {
    "1": "Registrar cliente",
    "2": "Registrar platillo",
    "3": "Registrar pedido",
    "4": "Reportes",
    "5": "Editar nombre evento",
    "6": "Salir"
}

def guardar_datos():
    with open(ARCH_CLIENTES, "w") as f:
        json.dump(clientes, f)
    with open(ARCH_PLATILLOS, "w") as f:
        json.dump(platillos, f)
    with open(ARCH_PEDIDOS, "w") as f:
        json.dump(pedidos, f)

def cargar_datos():
    global clientes, platillos, pedidos, contador_folio
    if not os.path.exists(ARCH_CLIENTES) and not os.path.exists(ARCH_PLATILLOS) and not os.path.exists(ARCH_PEDIDOS):
        print("Sistema iniciado sin datos previos")
        return
    try:
        if os.path.exists(ARCH_CLIENTES):
            with open(ARCH_CLIENTES, "r") as f:
                clientes = {int(k):v for k,v in json.load(f).items()}
        if os.path.exists(ARCH_PLATILLOS):
            with open(ARCH_PLATILLOS, "r") as f:
                platillos = {int(k):v for k,v in json.load(f).items()}
        if os.path.exists(ARCH_PEDIDOS):
            with open(ARCH_PEDIDOS, "r") as f:
                pedidos = {int(k):v for k,v in json.load(f).items()}
        if pedidos:
            contador_folio = max(pedidos.keys()) + 1
    except:
        print("Error crítico en archivos")
        exit()

def pedir_numero(msg):
    while True:
        valor = input(msg + " (C cancelar): ").strip()
        if valor.upper() == "C":
            return None
        try:
            return int(valor)
        except:
            print("Número inválido")

def pedir_fecha(msg):
    while True:
        valor = input(msg + " (dd/mm/aaaa | C cancelar): ").strip()
        if valor.upper() == "C":
            return None
        try:
            return datetime.datetime.strptime(valor, FORMATO_FECHA).date()
        except:
            print("Formato incorrecto")

def texto_valido(txt):
    return txt.strip() != ""

def mostrar_clientes():
    print("\nCLIENTES")
    for c,d in sorted(clientes.items(), key=lambda x: x[1]["apellido"].lower()):
        print(c, "-", d["apellido"], d["nombre"])

def mostrar_platillos():
    print("\nPLATILLOS")
    for p,n in sorted(platillos.items(), key=lambda x: x[1].lower()):
        print(p, "-", n)

def registrar_cliente():
    nuevo = max(clientes.keys()) + 1 if clientes else 101
    while True:
        nombre = input("Nombre: ")
        if texto_valido(nombre):
            break
    while True:
        apellido = input("Apellido: ")
        if texto_valido(apellido):
            break
    clientes[nuevo] = {"nombre": nombre.strip(), "apellido": apellido.strip()}
    print("Cliente registrado", nuevo)

def registrar_platillo():
    nuevo = max(platillos.keys()) + 1 if platillos else 501
    while True:
        nombre = input("Platillo: ")
        if texto_valido(nombre):
            break
    platillos[nuevo] = nombre.strip()
    print("Platillo registrado", nuevo)

def registrar_pedido():
    global contador_folio
    if not clientes or not platillos:
        print("Registra clientes y platillos primero")
        return

    while True:
        mostrar_clientes()
        id_cli = pedir_numero("ID cliente")
        if id_cli is None:
            return
        if id_cli in clientes:
            break

    fecha = pedir_fecha("Fecha evento")
    if not fecha:
        return
    if fecha < FECHA_ACTUAL + datetime.timedelta(days=2):
        print("Debe ser mínimo 2 días")
        return

    while True:
        t = input("Turno M/T/N: ").upper()
        if t in TURNOS:
            turno = TURNOS[t]
            break

    for p in pedidos.values():
        if p["cliente"]==id_cli and p["fecha"]==fecha.strftime(FORMATO_FECHA) and p["turno"]==turno:
            print("Ya existe pedido")
            return
    lista = []

    while True:
        mostrar_platillos()
        id_plat = pedir_numero("ID platillo")
        if id_plat is None:
            break
        if id_plat not in platillos:
            continue

        porciones = pedir_numero("Porciones")
        if porciones is None or porciones<=0:
            continue

        existe = False
        for item in lista:
            if item["platillo"] == id_plat:
                item["porciones"] += porciones
                existe = True
                break
        if not existe:
            lista.append({"platillo":id_plat,"porciones":porciones})

    if not lista:
        return

    while True:
        evento = input("Evento: ")
        if texto_valido(evento):
            break
    pedidos[contador_folio] = {
        "cliente":id_cli,
        "fecha":fecha.strftime(FORMATO_FECHA),
        "turno":turno,
        "evento":evento.strip(),
        "platillos":lista
    }

    print("Folio", contador_folio)
    contador_folio += 1

def reporte_rango():
    ini = pedir_fecha("Fecha inicio")
    fin = pedir_fecha("Fecha fin")
    if not ini or not fin:
        return

    encontrados=False

    for f,p in pedidos.items():
        if ini.strftime(FORMATO_FECHA) <= p["fecha"] <= fin.strftime(FORMATO_FECHA):
            cli=clientes[p["cliente"]]
            print(f, cli["apellido"], cli["nombre"], p["evento"], p["fecha"])
            for pl in p["platillos"]:
                print(" ", platillos[pl["platillo"]], pl["porciones"])
            encontrados=True

    if not encontrados:
        print("Sin datos")
        
def reporte_clientes():
    for c,d in sorted(clientes.items(), key=lambda x: x[1]["apellido"].lower()):
        print(c, d["apellido"], d["nombre"])

def reporte_platillos():
    for p,n in sorted(platillos.items(), key=lambda x: x[1].lower()):
        print(p, n)

def reporte_estadistico():
    ini = pedir_fecha("Fecha inicio")
    fin = pedir_fecha("Fecha fin")
    if not ini or not fin:
        return

    conteo = {}

    for p in pedidos.values():
        if ini.strftime(FORMATO_FECHA) <= p["fecha"] <= fin.strftime(FORMATO_FECHA):
            for pl in p["platillos"]:
                nombre = platillos[pl["platillo"]]
                conteo[nombre] = conteo.get(nombre,0)+pl["porciones"]

    for k,v in sorted(conteo.items(), key=lambda x: x[1], reverse=True):
        print(k, v)

def reportes():
    print("1. Rango")
    print("2. Clientes")
    print("3. Platillos")
    print("4. Estadistico")
    op = input("Opción: ")
    if op=="1":
        reporte_rango()
    elif op=="2":
        reporte_clientes()
    elif op=="3":
        reporte_platillos()
    elif op=="4":
        reporte_estadistico()

def editar_evento():
    ini = pedir_fecha("Inicio")
    fin = pedir_fecha("Fin")
    if not ini or not fin:
        return

    rango={f:p for f,p in pedidos.items() if ini.strftime(FORMATO_FECHA)<=p["fecha"]<=fin.strftime(FORMATO_FECHA)}

    for f,p in rango.items():
        print(f, p["evento"], p["fecha"])

    fol=pedir_numero("Folio")
    if fol not in rango:
        return

    while True:
        nuevo=input("Nuevo nombre: ")
        if texto_valido(nuevo):
            break

    pedidos[fol]["evento"]=nuevo.strip()

cargar_datos()

while True:
    print("\nMENU")
    for k,v in menu.items():
        print(k,v)

    op=input("Opción: ")

    if op=="1":
        registrar_cliente()
    elif op=="2":
        registrar_platillo()
    elif op=="3":
        registrar_pedido()
    elif op=="4":
        reportes()
    elif op=="5":
        editar_evento()
    elif op=="6":
        guardar_datos()
        print("Datos guardados")
        break