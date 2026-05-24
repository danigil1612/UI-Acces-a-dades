# Guió curt del vídeo

## 1. Presentació de l'app

Aquesta aplicació és un back-office de Fórmula 1. Permet gestionar conductors, cotxes, patrocinadors, pistes, curses, pneumàtics i resultats. La UI està feta amb Rich i treballa contra els repositoris i la unitat de treball.

Relacions del domini:

- 1:1 entre conductor i cotxe.
- 1:N entre pista i cursa.
- N:M entre conductor i patrocinador.
- N:M amb atributs entre resultat i pneumàtic, mitjançant ResultatPneumatic.

## 2. Recorregut pel codi

Fitxers principals:

- `src/domain/models.py`: models SQLAlchemy.
- `src/domain/repositories.py`: CRUD, consultes específiques i Unit of Work.
- `src/ui/main.py`: menús de consola, formularis i taules Rich.

Explicació clau:

- Cada menú obre operacions del repositori corresponent.
- Les operacions creen una `UnitatDeTreball`.
- El commit es fa només quan l'operació acaba bé.
- Les relacions es gestionen seleccionant IDs d'entitats relacionades.

## 3. Demo

Ordre recomanat:

1. Executar `alembic upgrade head`.
2. Executar `python -m ui.main`.
3. Entrar a `Carregar dades de demo`.
4. Mostrar `Relacions`.
5. Crear, llegir, actualitzar i eliminar un registre senzill, per exemple un pneumàtic.
6. Buscar conductors per nom o nacionalitat.
7. Mostrar paginació de resultats.
8. Afegir un pneumàtic a un resultat per demostrar N:M amb atributs.
9. Afegir un patrocinador a un conductor per demostrar N:M.
