from __future__ import annotations

from datetime import date
from typing import Callable, Iterable, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from domain.models import Conductor, Cotxe, Cursa, Patrocinador, Pista, Pneumatic, ResultatCursa
from domain.repositories import UnitatDeTreball

console = Console(emoji=False)


def pausa() -> None:
    Prompt.ask("Prem Enter per continuar", default="")


def llegir_text(camp: str, valor_actual: Optional[str] = None, obligatori: bool = True) -> str:
    while True:
        if valor_actual is None:
            valor = Prompt.ask(camp, default="" if not obligatori else None)
        else:
            valor = Prompt.ask(camp, default=str(valor_actual))
        valor = valor.strip()
        if valor or not obligatori:
            return valor
        console.print("[red]Aquest camp és obligatori.[/red]")


def llegir_int(camp: str, valor_actual: Optional[int] = None) -> int:
    while True:
        text = Prompt.ask(camp, default=str(valor_actual) if valor_actual is not None else None)
        try:
            return int(text)
        except ValueError:
            console.print("[red]Introdueix un nombre enter.[/red]")


def llegir_float(camp: str, valor_actual: Optional[float] = None) -> float:
    while True:
        text = Prompt.ask(camp, default=str(valor_actual) if valor_actual is not None else None)
        try:
            return float(text.replace(",", "."))
        except ValueError:
            console.print("[red]Introdueix un nombre decimal vàlid.[/red]")


def llegir_data(camp: str, valor_actual: Optional[date] = None) -> date:
    while True:
        text = Prompt.ask(camp, default=valor_actual.isoformat() if valor_actual else None)
        try:
            return date.fromisoformat(text)
        except ValueError:
            console.print("[red]Format incorrecte. Usa AAAA-MM-DD.[/red]")


def imprimir_resultat(missatge: str) -> None:
    console.print(f"[green]{missatge}[/green]")


def imprimir_error(error: Exception) -> None:
    console.print(f"[red]Error: {error}[/red]")


def taula_conductors(conductors: Sequence[Conductor]) -> Table:
    taula = Table(title="Conductors")
    for columna in ("ID", "Nom", "Nacionalitat", "Número", "Cotxe", "Patrocinadors"):
        taula.add_column(columna)
    for c in conductors:
        patrocinadors = ", ".join(p.nom for p in c.patrocinadors) or "-"
        taula.add_row(
            str(c.id_driver),
            c.nom,
            c.nacionalitat,
            str(c.numero),
            c.cotxe.codi_xassis if c.cotxe else "-",
            patrocinadors,
        )
    return taula


def taula_cotxes(cotxes: Sequence[Cotxe]) -> Table:
    taula = Table(title="Cotxes")
    for columna in ("ID", "Xassís", "Motor", "CV", "Pes", "Conductor"):
        taula.add_column(columna)
    for c in cotxes:
        taula.add_row(
            str(c.id_cotxe),
            c.codi_xassis,
            c.proveidor_de_motors,
            str(c.potencia_cv),
            str(c.pes_kg),
            c.conductor.nom if c.conductor else "-",
        )
    return taula


def taula_patrocinadors(patrocinadors: Sequence[Patrocinador]) -> Table:
    taula = Table(title="Patrocinadors")
    for columna in ("ID", "Nom", "Sector", "País", "Conductors"):
        taula.add_column(columna)
    for p in patrocinadors:
        conductors = ", ".join(c.nom for c in p.conductors) or "-"
        taula.add_row(str(p.id_sponsor), p.nom, p.sector, p.pais, conductors)
    return taula


def taula_pistes(pistes: Sequence[Pista]) -> Table:
    taula = Table(title="Pistes")
    for columna in ("ID", "Nom", "País", "Longitud km", "Curses"):
        taula.add_column(columna)
    for p in pistes:
        taula.add_row(str(p.id_track), p.nom, p.pais, str(p.longitud_km), str(len(p.curses)))
    return taula


def taula_curses(curses: Sequence[Cursa]) -> Table:
    taula = Table(title="Curses")
    for columna in ("ID", "Gran Premi", "Data", "Temporada", "Pista"):
        taula.add_column(columna)
    for c in curses:
        taula.add_row(
            str(c.id_race),
            c.nom_del_gran_premi,
            c.data.isoformat(),
            str(c.temporada),
            c.pista.nom if c.pista else "-",
        )
    return taula


def taula_pneumatics(pneumatics: Sequence[Pneumatic]) -> Table:
    taula = Table(title="Pneumàtics")
    for columna in ("ID", "Compost", "Descripció"):
        taula.add_column(columna)
    for p in pneumatics:
        taula.add_row(str(p.id_tyre), p.nom_compost, p.descripcio or "-")
    return taula


def resum_pneumatics(resultat: ResultatCursa) -> str:
    usos = sorted(resultat.usos_pneumatics, key=lambda u: u.periode)
    if not usos:
        return "-"
    return "; ".join(
        f"P{u.periode}: {u.pneumatic.nom_compost} ({u.nombre_de_voltes} voltes, ús {u.numero_us})"
        for u in usos
    )


def taula_resultats(resultats: Sequence[ResultatCursa]) -> Table:
    taula = Table(title="Resultats de cursa")
    for columna in ("ID", "Posició", "Punts", "Temps", "Conductor", "Cursa", "Pneumàtics"):
        taula.add_column(columna)
    for r in resultats:
        taula.add_row(
            str(r.id_result),
            str(r.posicio_final),
            str(r.punts),
            r.temps_total or "-",
            r.conductor.nom if r.conductor else "-",
            r.cursa.nom_del_gran_premi if r.cursa else "-",
            resum_pneumatics(r),
        )
    return taula


def mostrar_taula(titol: str, items: Sequence, constructor: Callable[[Sequence], Table]) -> None:
    if not items:
        console.print(f"[yellow]No hi ha registres a {titol}.[/yellow]")
        return
    console.print(constructor(items))


def executar(operacio: Callable[[], None]) -> None:
    try:
        operacio()
    except (ValueError, SQLAlchemyError) as error:
        imprimir_error(error)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operació cancel·lada.[/yellow]")
    pausa()


def menu_principal() -> None:
    opcions = {
        "1": ("Conductors", menu_conductors),
        "2": ("Cotxes", menu_cotxes),
        "3": ("Patrocinadors", menu_patrocinadors),
        "4": ("Pistes", menu_pistes),
        "5": ("Curses", menu_curses),
        "6": ("Pneumàtics", menu_pneumatics),
        "7": ("Resultats", menu_resultats),
        "8": ("Relacions", menu_relacions),
        "9": ("Carregar dades de demo", carregar_dades_demo),
        "0": ("Sortir", None),
    }
    while True:
        console.print(Panel.fit("Back Office F1", subtitle="Repository + Unit of Work + Rich UI"))
        for clau, (text, _) in opcions.items():
            console.print(f"[cyan]{clau}[/cyan]. {text}")
        tria = Prompt.ask("Opció", choices=list(opcions.keys()))
        if tria == "0":
            break
        funcio = opcions[tria][1]
        if funcio is carregar_dades_demo:
            executar(funcio)
        else:
            funcio()


def menu_generador(titol: str, opcions: dict[str, tuple[str, Callable[[], None]]]) -> None:
    while True:
        console.print(Panel.fit(titol))
        for clau, (text, _) in opcions.items():
            console.print(f"[cyan]{clau}[/cyan]. {text}")
        console.print("[cyan]0[/cyan]. Tornar")
        tria = Prompt.ask("Opció", choices=[*opcions.keys(), "0"])
        if tria == "0":
            return
        executar(opcions[tria][1])


def menu_conductors() -> None:
    menu_generador(
        "Conductors",
        {
            "1": ("Crear", crear_conductor),
            "2": ("Llistar", llistar_conductors),
            "3": ("Llegir per ID", llegir_conductor),
            "4": ("Actualitzar", actualitzar_conductor),
            "5": ("Eliminar", eliminar_conductor),
            "6": ("Buscar per nom", buscar_conductor_nom),
            "7": ("Buscar per número", buscar_conductor_numero),
            "8": ("Buscar per nacionalitat", buscar_conductor_nacionalitat),
            "9": ("Afegir patrocinador a conductor", afegir_patrocinador_a_conductor),
            "10": ("Treure patrocinador de conductor", treure_patrocinador_de_conductor),
        },
    )


def menu_cotxes() -> None:
    menu_generador(
        "Cotxes",
        {
            "1": ("Crear", crear_cotxe),
            "2": ("Llistar", llistar_cotxes),
            "3": ("Llegir per ID", llegir_cotxe),
            "4": ("Actualitzar", actualitzar_cotxe),
            "5": ("Eliminar", eliminar_cotxe),
            "6": ("Buscar per xassís", buscar_cotxe_xassis),
            "7": ("Buscar per motor", buscar_cotxe_motor),
        },
    )


def menu_patrocinadors() -> None:
    menu_generador(
        "Patrocinadors",
        {
            "1": ("Crear", crear_patrocinador),
            "2": ("Llistar", llistar_patrocinadors),
            "3": ("Llegir per ID", llegir_patrocinador),
            "4": ("Actualitzar", actualitzar_patrocinador),
            "5": ("Eliminar", eliminar_patrocinador),
            "6": ("Buscar per nom", buscar_patrocinador_nom),
            "7": ("Buscar per sector", buscar_patrocinador_sector),
        },
    )


def menu_pistes() -> None:
    menu_generador(
        "Pistes",
        {
            "1": ("Crear", crear_pista),
            "2": ("Llistar", llistar_pistes),
            "3": ("Llegir per ID", llegir_pista),
            "4": ("Actualitzar", actualitzar_pista),
            "5": ("Eliminar", eliminar_pista),
            "6": ("Buscar per nom", buscar_pista_nom),
            "7": ("Buscar per país", buscar_pista_pais),
        },
    )


def menu_curses() -> None:
    menu_generador(
        "Curses",
        {
            "1": ("Crear", crear_cursa),
            "2": ("Llistar", llistar_curses),
            "3": ("Llegir per ID", llegir_cursa),
            "4": ("Actualitzar", actualitzar_cursa),
            "5": ("Eliminar", eliminar_cursa),
            "6": ("Buscar per temporada", buscar_cursa_temporada),
            "7": ("Buscar per Gran Premi", buscar_cursa_gran_premi),
        },
    )


def menu_pneumatics() -> None:
    menu_generador(
        "Pneumàtics",
        {
            "1": ("Crear", crear_pneumatic),
            "2": ("Llistar", llistar_pneumatics),
            "3": ("Llegir per ID", llegir_pneumatic),
            "4": ("Actualitzar", actualitzar_pneumatic),
            "5": ("Eliminar", eliminar_pneumatic),
            "6": ("Buscar per compost", buscar_pneumatic_compost),
        },
    )


def menu_resultats() -> None:
    menu_generador(
        "Resultats",
        {
            "1": ("Crear", crear_resultat),
            "2": ("Llistar", llistar_resultats),
            "3": ("Llegir per ID", llegir_resultat),
            "4": ("Actualitzar", actualitzar_resultat),
            "5": ("Eliminar", eliminar_resultat),
            "6": ("Buscar per conductor", buscar_resultat_conductor),
            "7": ("Buscar per cursa", buscar_resultat_cursa),
            "8": ("Veure podi", buscar_podi),
            "9": ("Paginació", paginar_resultats),
            "10": ("Afegir pneumàtic al resultat", afegir_pneumatic_a_resultat),
        },
    )


def crear_conductor() -> None:
    with UnitatDeTreball() as uow:
        conductor = Conductor(
            nom=llegir_text("Nom"),
            nacionalitat=llegir_text("Nacionalitat"),
            numero=llegir_int("Número"),
        )
        uow.conductors.add(conductor)
        uow.commit()
        imprimir_resultat(f"Conductor creat amb ID {conductor.id_driver}.")


def llistar_conductors() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)


def llegir_conductor() -> None:
    with UnitatDeTreball() as uow:
        conductor = uow.conductors.get(llegir_int("ID conductor"))
        mostrar_taula("conductors", [conductor] if conductor else [], taula_conductors)


def actualitzar_conductor() -> None:
    with UnitatDeTreball() as uow:
        conductor = uow.conductors.get(llegir_int("ID conductor"))
        if conductor is None:
            raise ValueError("Conductor no trobat.")
        conductor.nom = llegir_text("Nom", conductor.nom)
        conductor.nacionalitat = llegir_text("Nacionalitat", conductor.nacionalitat)
        conductor.numero = llegir_int("Número", conductor.numero)
        uow.conductors.update(conductor)
        uow.commit()
        imprimir_resultat("Conductor actualitzat.")


def eliminar_conductor() -> None:
    with UnitatDeTreball() as uow:
        id_driver = llegir_int("ID conductor")
        if Confirm.ask("Segur que vols eliminar-lo?"):
            uow.conductors.delete(id_driver)
            uow.commit()
            imprimir_resultat("Conductor eliminat.")


def buscar_conductor_nom() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_by_nom(llegir_text("Text del nom")), taula_conductors)


def buscar_conductor_numero() -> None:
    with UnitatDeTreball() as uow:
        conductor = uow.conductors.get_by_numero(llegir_int("Número"))
        mostrar_taula("conductors", [conductor] if conductor else [], taula_conductors)


def buscar_conductor_nacionalitat() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_by_nacionalitat(llegir_text("Nacionalitat")), taula_conductors)


def afegir_patrocinador_a_conductor() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        id_driver = llegir_int("ID conductor")
        mostrar_taula("patrocinadors", uow.patrocinadors.get_all(), taula_patrocinadors)
        id_sponsor = llegir_int("ID patrocinador")
        uow.conductors.afegir_patrocinador(id_driver, id_sponsor)
        uow.commit()
        imprimir_resultat("Relació N:M creada.")


def treure_patrocinador_de_conductor() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        id_driver = llegir_int("ID conductor")
        mostrar_taula("patrocinadors", uow.patrocinadors.get_all(), taula_patrocinadors)
        id_sponsor = llegir_int("ID patrocinador")
        uow.conductors.treure_patrocinador(id_driver, id_sponsor)
        uow.commit()
        imprimir_resultat("Relació N:M eliminada.")


def crear_cotxe() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        cotxe = Cotxe(
            codi_xassis=llegir_text("Codi xassís"),
            proveidor_de_motors=llegir_text("Proveïdor de motors"),
            potencia_cv=llegir_int("Potència CV"),
            pes_kg=llegir_float("Pes kg"),
            id_driver=llegir_int("ID conductor"),
        )
        uow.cotxes.add(cotxe)
        uow.commit()
        imprimir_resultat(f"Cotxe creat amb ID {cotxe.id_cotxe}. Relació 1:1 assignada.")


def llistar_cotxes() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("cotxes", uow.cotxes.get_all(), taula_cotxes)


def llegir_cotxe() -> None:
    with UnitatDeTreball() as uow:
        cotxe = uow.cotxes.get(llegir_int("ID cotxe"))
        mostrar_taula("cotxes", [cotxe] if cotxe else [], taula_cotxes)


def actualitzar_cotxe() -> None:
    with UnitatDeTreball() as uow:
        cotxe = uow.cotxes.get(llegir_int("ID cotxe"))
        if cotxe is None:
            raise ValueError("Cotxe no trobat.")
        cotxe.codi_xassis = llegir_text("Codi xassís", cotxe.codi_xassis)
        cotxe.proveidor_de_motors = llegir_text("Proveïdor de motors", cotxe.proveidor_de_motors)
        cotxe.potencia_cv = llegir_int("Potència CV", cotxe.potencia_cv)
        cotxe.pes_kg = llegir_float("Pes kg", cotxe.pes_kg)
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        cotxe.id_driver = llegir_int("ID conductor", cotxe.id_driver)
        uow.cotxes.update(cotxe)
        uow.commit()
        imprimir_resultat("Cotxe actualitzat.")


def eliminar_cotxe() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-lo?"):
            uow.cotxes.delete(llegir_int("ID cotxe"))
            uow.commit()
            imprimir_resultat("Cotxe eliminat.")


def buscar_cotxe_xassis() -> None:
    with UnitatDeTreball() as uow:
        cotxe = uow.cotxes.get_by_codi_xassis(llegir_text("Codi xassís"))
        mostrar_taula("cotxes", [cotxe] if cotxe else [], taula_cotxes)


def buscar_cotxe_motor() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("cotxes", uow.cotxes.get_by_proveidor_de_motors(llegir_text("Motor")), taula_cotxes)


def crear_patrocinador() -> None:
    with UnitatDeTreball() as uow:
        patrocinador = Patrocinador(
            nom=llegir_text("Nom"),
            sector=llegir_text("Sector"),
            pais=llegir_text("País"),
        )
        uow.patrocinadors.add(patrocinador)
        uow.commit()
        imprimir_resultat(f"Patrocinador creat amb ID {patrocinador.id_sponsor}.")


def llistar_patrocinadors() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("patrocinadors", uow.patrocinadors.get_all(), taula_patrocinadors)


def llegir_patrocinador() -> None:
    with UnitatDeTreball() as uow:
        patrocinador = uow.patrocinadors.get(llegir_int("ID patrocinador"))
        mostrar_taula("patrocinadors", [patrocinador] if patrocinador else [], taula_patrocinadors)


def actualitzar_patrocinador() -> None:
    with UnitatDeTreball() as uow:
        patrocinador = uow.patrocinadors.get(llegir_int("ID patrocinador"))
        if patrocinador is None:
            raise ValueError("Patrocinador no trobat.")
        patrocinador.nom = llegir_text("Nom", patrocinador.nom)
        patrocinador.sector = llegir_text("Sector", patrocinador.sector)
        patrocinador.pais = llegir_text("País", patrocinador.pais)
        uow.patrocinadors.update(patrocinador)
        uow.commit()
        imprimir_resultat("Patrocinador actualitzat.")


def eliminar_patrocinador() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-lo?"):
            uow.patrocinadors.delete(llegir_int("ID patrocinador"))
            uow.commit()
            imprimir_resultat("Patrocinador eliminat.")


def buscar_patrocinador_nom() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("patrocinadors", uow.patrocinadors.get_by_nom(llegir_text("Text del nom")), taula_patrocinadors)


def buscar_patrocinador_sector() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("patrocinadors", uow.patrocinadors.get_by_sector(llegir_text("Sector")), taula_patrocinadors)


def crear_pista() -> None:
    with UnitatDeTreball() as uow:
        pista = Pista(nom=llegir_text("Nom"), pais=llegir_text("País"), longitud_km=llegir_float("Longitud km"))
        uow.pistes.add(pista)
        uow.commit()
        imprimir_resultat(f"Pista creada amb ID {pista.id_track}.")


def llistar_pistes() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("pistes", uow.pistes.get_all(), taula_pistes)


def llegir_pista() -> None:
    with UnitatDeTreball() as uow:
        pista = uow.pistes.get(llegir_int("ID pista"))
        mostrar_taula("pistes", [pista] if pista else [], taula_pistes)


def actualitzar_pista() -> None:
    with UnitatDeTreball() as uow:
        pista = uow.pistes.get(llegir_int("ID pista"))
        if pista is None:
            raise ValueError("Pista no trobada.")
        pista.nom = llegir_text("Nom", pista.nom)
        pista.pais = llegir_text("País", pista.pais)
        pista.longitud_km = llegir_float("Longitud km", pista.longitud_km)
        uow.pistes.update(pista)
        uow.commit()
        imprimir_resultat("Pista actualitzada.")


def eliminar_pista() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-la?"):
            uow.pistes.delete(llegir_int("ID pista"))
            uow.commit()
            imprimir_resultat("Pista eliminada.")


def buscar_pista_nom() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("pistes", uow.pistes.get_by_nom(llegir_text("Text del nom")), taula_pistes)


def buscar_pista_pais() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("pistes", uow.pistes.get_by_pais(llegir_text("País")), taula_pistes)


def crear_cursa() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("pistes", uow.pistes.get_all(), taula_pistes)
        cursa = Cursa(
            nom_del_gran_premi=llegir_text("Gran Premi"),
            data=llegir_data("Data AAAA-MM-DD"),
            temporada=llegir_int("Temporada"),
            id_track=llegir_int("ID pista"),
        )
        uow.curses.add(cursa)
        uow.commit()
        imprimir_resultat(f"Cursa creada amb ID {cursa.id_race}. Relació 1:N assignada.")


def llistar_curses() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("curses", uow.curses.get_all(), taula_curses)


def llegir_cursa() -> None:
    with UnitatDeTreball() as uow:
        cursa = uow.curses.get(llegir_int("ID cursa"))
        mostrar_taula("curses", [cursa] if cursa else [], taula_curses)


def actualitzar_cursa() -> None:
    with UnitatDeTreball() as uow:
        cursa = uow.curses.get(llegir_int("ID cursa"))
        if cursa is None:
            raise ValueError("Cursa no trobada.")
        cursa.nom_del_gran_premi = llegir_text("Gran Premi", cursa.nom_del_gran_premi)
        cursa.data = llegir_data("Data AAAA-MM-DD", cursa.data)
        cursa.temporada = llegir_int("Temporada", cursa.temporada)
        mostrar_taula("pistes", uow.pistes.get_all(), taula_pistes)
        cursa.id_track = llegir_int("ID pista", cursa.id_track)
        uow.curses.update(cursa)
        uow.commit()
        imprimir_resultat("Cursa actualitzada.")


def eliminar_cursa() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-la?"):
            uow.curses.delete(llegir_int("ID cursa"))
            uow.commit()
            imprimir_resultat("Cursa eliminada.")


def buscar_cursa_temporada() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("curses", uow.curses.get_by_temporada(llegir_int("Temporada")), taula_curses)


def buscar_cursa_gran_premi() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("curses", uow.curses.get_by_gran_premi(llegir_text("Text del Gran Premi")), taula_curses)


def crear_pneumatic() -> None:
    with UnitatDeTreball() as uow:
        pneumatic = Pneumatic(nom_compost=llegir_text("Nom compost"), descripcio=llegir_text("Descripció", obligatori=False) or None)
        uow.pneumatics.add(pneumatic)
        uow.commit()
        imprimir_resultat(f"Pneumàtic creat amb ID {pneumatic.id_tyre}.")


def llistar_pneumatics() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("pneumàtics", uow.pneumatics.get_all(), taula_pneumatics)


def llegir_pneumatic() -> None:
    with UnitatDeTreball() as uow:
        pneumatic = uow.pneumatics.get(llegir_int("ID pneumàtic"))
        mostrar_taula("pneumàtics", [pneumatic] if pneumatic else [], taula_pneumatics)


def actualitzar_pneumatic() -> None:
    with UnitatDeTreball() as uow:
        pneumatic = uow.pneumatics.get(llegir_int("ID pneumàtic"))
        if pneumatic is None:
            raise ValueError("Pneumàtic no trobat.")
        pneumatic.nom_compost = llegir_text("Nom compost", pneumatic.nom_compost)
        pneumatic.descripcio = llegir_text("Descripció", pneumatic.descripcio or "", obligatori=False) or None
        uow.pneumatics.update(pneumatic)
        uow.commit()
        imprimir_resultat("Pneumàtic actualitzat.")


def eliminar_pneumatic() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-lo?"):
            uow.pneumatics.delete(llegir_int("ID pneumàtic"))
            uow.commit()
            imprimir_resultat("Pneumàtic eliminat.")


def buscar_pneumatic_compost() -> None:
    with UnitatDeTreball() as uow:
        pneumatic = uow.pneumatics.get_by_nom_compost(llegir_text("Nom compost"))
        mostrar_taula("pneumàtics", [pneumatic] if pneumatic else [], taula_pneumatics)


def crear_resultat() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        id_driver = llegir_int("ID conductor")
        mostrar_taula("curses", uow.curses.get_all(), taula_curses)
        id_race = llegir_int("ID cursa")
        resultat = ResultatCursa(
            posicio_final=llegir_int("Posició final"),
            punts=llegir_float("Punts"),
            temps_total=llegir_text("Temps total", obligatori=False) or None,
            id_driver=id_driver,
            id_race=id_race,
        )
        uow.resultats.add(resultat)
        uow.commit()
        imprimir_resultat(f"Resultat creat amb ID {resultat.id_result}.")


def llistar_resultats() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("resultats", uow.resultats.get_all(), taula_resultats)


def llegir_resultat() -> None:
    with UnitatDeTreball() as uow:
        resultat = uow.resultats.get(llegir_int("ID resultat"))
        mostrar_taula("resultats", [resultat] if resultat else [], taula_resultats)


def actualitzar_resultat() -> None:
    with UnitatDeTreball() as uow:
        resultat = uow.resultats.get(llegir_int("ID resultat"))
        if resultat is None:
            raise ValueError("Resultat no trobat.")
        resultat.posicio_final = llegir_int("Posició final", resultat.posicio_final)
        resultat.punts = llegir_float("Punts", resultat.punts)
        resultat.temps_total = llegir_text("Temps total", resultat.temps_total or "", obligatori=False) or None
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        resultat.id_driver = llegir_int("ID conductor", resultat.id_driver)
        mostrar_taula("curses", uow.curses.get_all(), taula_curses)
        resultat.id_race = llegir_int("ID cursa", resultat.id_race)
        uow.resultats.update(resultat)
        uow.commit()
        imprimir_resultat("Resultat actualitzat.")


def eliminar_resultat() -> None:
    with UnitatDeTreball() as uow:
        if Confirm.ask("Segur que vols eliminar-lo?"):
            uow.resultats.delete(llegir_int("ID resultat"))
            uow.commit()
            imprimir_resultat("Resultat eliminat.")


def buscar_resultat_conductor() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        mostrar_taula("resultats", uow.resultats.get_by_conductor(llegir_int("ID conductor")), taula_resultats)


def buscar_resultat_cursa() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("curses", uow.curses.get_all(), taula_curses)
        mostrar_taula("resultats", uow.resultats.get_by_cursa(llegir_int("ID cursa")), taula_resultats)


def buscar_podi() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("curses", uow.curses.get_all(), taula_curses)
        mostrar_taula("resultats", uow.resultats.get_podi(llegir_int("ID cursa")), taula_resultats)


def paginar_resultats() -> None:
    with UnitatDeTreball() as uow:
        pagina = llegir_int("Pàgina")
        mida = llegir_int("Mida de pàgina")
        mostrar_taula("resultats", uow.resultats.get_paginated(pagina, mida), taula_resultats)


def afegir_pneumatic_a_resultat() -> None:
    with UnitatDeTreball() as uow:
        mostrar_taula("resultats", uow.resultats.get_all(), taula_resultats)
        id_result = llegir_int("ID resultat")
        mostrar_taula("pneumàtics", uow.pneumatics.get_all(), taula_pneumatics)
        id_tyre = llegir_int("ID pneumàtic")
        uow.resultats.afegir_pneumatic_a_resultat(
            id_result=id_result,
            id_tyre=id_tyre,
            periode=llegir_int("Període/stint"),
            nombre_de_voltes=llegir_int("Nombre de voltes"),
            numero_us=llegir_int("Número d'ús"),
        )
        uow.commit()
        imprimir_resultat("Relació N:M amb atributs creada.")


def menu_relacions() -> None:
    with UnitatDeTreball() as uow:
        console.print(Panel("1:1: un conductor pot tenir un sol cotxe i un cotxe pertany a un conductor."))
        mostrar_taula("cotxes", uow.cotxes.get_all(), taula_cotxes)
        console.print(Panel("1:N: una pista pot tenir moltes curses."))
        mostrar_taula("pistes", uow.pistes.get_all(), taula_pistes)
        console.print(Panel("N:M: un conductor pot tenir molts patrocinadors i un patrocinador pot estar amb molts conductors."))
        mostrar_taula("conductors", uow.conductors.get_all(), taula_conductors)
        console.print(Panel("N:M amb atributs: un resultat usa diversos pneumàtics i cada ús guarda període, voltes i número d'ús."))
        mostrar_taula("resultats", uow.resultats.get_all(), taula_resultats)
    pausa()


def carregar_dades_demo() -> None:
    with UnitatDeTreball() as uow:
        if not uow.conductors.get_by_numero(1):
            verstappen = uow.conductors.add(Conductor(nom="Max Verstappen", nacionalitat="Països Baixos", numero=1))
        else:
            verstappen = uow.conductors.get_by_numero(1)
        if not uow.conductors.get_by_numero(16):
            leclerc = uow.conductors.add(Conductor(nom="Charles Leclerc", nacionalitat="Mònaco", numero=16))
        else:
            leclerc = uow.conductors.get_by_numero(16)

        oracle = next(iter(uow.patrocinadors.get_by_nom("Oracle")), None)
        if oracle is None:
            oracle = uow.patrocinadors.add(Patrocinador(nom="Oracle", sector="Tecnologia", pais="Estats Units"))
        shell = next(iter(uow.patrocinadors.get_by_nom("Shell")), None)
        if shell is None:
            shell = uow.patrocinadors.add(Patrocinador(nom="Shell", sector="Energia", pais="Països Baixos"))

        if uow.cotxes.get_by_codi_xassis("RB20-01") is None:
            uow.cotxes.add(Cotxe(codi_xassis="RB20-01", proveidor_de_motors="Honda RBPT", potencia_cv=1000, pes_kg=798, id_driver=verstappen.id_driver))
        if uow.cotxes.get_by_codi_xassis("SF24-16") is None:
            uow.cotxes.add(Cotxe(codi_xassis="SF24-16", proveidor_de_motors="Ferrari", potencia_cv=1000, pes_kg=798, id_driver=leclerc.id_driver))

        monaco = next(iter(uow.pistes.get_by_nom("Mònaco")), None)
        if monaco is None:
            monaco = uow.pistes.add(Pista(nom="Circuit de Mònaco", pais="Mònaco", longitud_km=3.337))
        gp = next(iter(uow.curses.get_by_gran_premi("Mònaco")), None)
        if gp is None:
            gp = uow.curses.add(Cursa(nom_del_gran_premi="Gran Premi de Mònaco", data=date(2024, 5, 26), temporada=2024, id_track=monaco.id_track))

        dur = uow.pneumatics.get_by_nom_compost("Dur")
        if dur is None:
            dur = uow.pneumatics.add(Pneumatic(nom_compost="Dur", descripcio="Compost dur"))
        mig = uow.pneumatics.get_by_nom_compost("Mitjà")
        if mig is None:
            mig = uow.pneumatics.add(Pneumatic(nom_compost="Mitjà", descripcio="Compost mitjà"))

        resultats_verstappen = uow.resultats.get_by_conductor(verstappen.id_driver)
        resultat = next((r for r in resultats_verstappen if r.id_race == gp.id_race), None)
        if resultat is None:
            resultat = uow.resultats.add(ResultatCursa(posicio_final=1, punts=25, temps_total="1:45:10.000", id_driver=verstappen.id_driver, id_race=gp.id_race))

        uow.conductors.afegir_patrocinador(verstappen.id_driver, oracle.id_sponsor)
        uow.conductors.afegir_patrocinador(leclerc.id_driver, shell.id_sponsor)

        if not any(us.periode == 1 for us in resultat.usos_pneumatics):
            uow.resultats.afegir_pneumatic_a_resultat(resultat.id_result, mig.id_tyre, 1, 38, 1)
        if not any(us.periode == 2 for us in resultat.usos_pneumatics):
            uow.resultats.afegir_pneumatic_a_resultat(resultat.id_result, dur.id_tyre, 2, 40, 1)

        uow.commit()
        imprimir_resultat("Dades de demo carregades.")


if __name__ == "__main__":
    menu_principal()
