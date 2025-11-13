# scripts/seed_events_flyer.py
from datetime import date, time
from app import app
from models import db
from models.evento import Evento

EVENTS = [
    dict(
        slug="presentacion-proyectos-1-2",
        titulo="Presentación de proyectos finales",
        descripcion_corta="Alumnas y alumnos 1º y 2º",
        tipo="Presentación",
        ponente_nombre=None,
        ponente_afiliacion=None,
        fecha=date(2025, 11, 28),
        hora_inicio=time(7, 0),
        hora_fin=time(10, 0),
        lugar="CUTLAJO - Edificio E",
        published=True,
    ),
    dict(
        slug="conferencia-ai-across-scales",
        titulo='Conferencia “Artificial Intelligence Across Scales”',
        descripcion_corta="",
        tipo="Conferencia",
        ponente_nombre="Mtro. Moisés Sotelo Rodríguez",
        ponente_afiliacion="BioDev Network",
        fecha=date(2025, 11, 28),
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
        lugar="Coworking CUTLAJO",
        published=True,
    ),
    dict(
        slug="cinco-voces-perspectivas",
        titulo="Cinco voces, cinco perspectivas, una pasión: Ingeniería Biomédica",
        descripcion_corta="Alumn@s de últimos semestres",
        tipo="Foro",
        ponente_nombre=None,
        ponente_afiliacion=None,
        fecha=date(2025, 11, 28),
        hora_inicio=time(11, 0),
        hora_fin=time(12, 0),
        lugar="Coworking CUTLAJO",
        published=True,
    ),
    dict(
        slug="taller-senales-ml-bradicardias",
        titulo='Taller “De Señales a Diagnósticos: ML en Bradicardias”',
        descripcion_corta="Taller práctico de machine learning en bradicardias",
        tipo="Taller",
        ponente_nombre=None,
        ponente_afiliacion=None,
        fecha=date(2025, 11, 28),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
        lugar="Coworking CUTLAJO",
        published=True,
    ),
    dict(
        slug="presentacion-modulares-finales",
        titulo="Presentación de Modulares y Proyectos finales",
        descripcion_corta="Alumn@s de Ingeniería Biomédica",
        tipo="Presentación",
        ponente_nombre=None,
        ponente_afiliacion=None,
        fecha=date(2025, 11, 28),
        hora_inicio=time(12, 0),
        hora_fin=time(15, 0),
        lugar="CUTLAJO - Edificio E",
        published=True,
    ),
    dict(
        slug="pelea-de-sumos",
        titulo="Pelea de sumos",
        descripcion_corta="Dentro de la agenda de presentación de proyectos modulares",
        tipo="Exhibición",
        ponente_nombre=None,
        ponente_afiliacion=None,
        fecha=date(2025, 11, 28),
        hora_inicio=time(13, 30),
        hora_fin=time(15, 0),
        lugar="Coworking CUTLAJO",
        published=True,
    ),
]

with app.app_context():
    db.session.query(Evento).delete()  # limpia tabla de eventos
    for d in EVENTS:
        db.session.add(Evento(**d))
    db.session.commit()
    print(f"✔ Se cargaron {len(EVENTS)} eventos (flyer exacto)")
