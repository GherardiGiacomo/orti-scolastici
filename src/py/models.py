from sqlalchemy.ext.automap import automap_base

from src.py.connection import engine


class CustomBase:
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        attributes: list[str] = [
            f"{column.name}={getattr(self, column.name)}"  # type: ignore # noqa: PGH003
            for column in self.__table__.columns  # type: ignore # noqa: PGH003
        ]
        return f"{self.__class__.__name__}({', '.join(attributes)})"


Base = automap_base(cls=CustomBase)
Base.prepare(autoload_with=engine, schema="orti_scolastici")


Istituti = Base.classes.istituti
Scuole = Base.classes.scuole
Persone = Base.classes.persone
PersoneScuola = Base.classes.persone_scuola
RiferimentiScuola = Base.classes.riferimenti_scuola
RiferimentiIstituto = Base.classes.riferimenti_istituto
Classi = Base.classes.classi
Finanziamenti = Base.classes.finanziamenti
PartecipantiFinanziamento = Base.classes.partecipanti_finanziamento
Orti = Base.classes.orti
Gruppi = Base.classes.gruppi
GruppiControllo = Base.classes.gruppi_controllo
Specie = Base.classes.specie
Repliche = Base.classes.repliche
Sensori = Base.classes.sensori
AssociazioniSensore = Base.classes.associazioni_sensore
Rilevazioni = Base.classes.rilevazioni
BiomassaStruttura = Base.classes.biomassa_struttura
AlterazioniFiorituraFruttificazione = Base.classes.alterazioni_fioritura_fruttificazione
AltriDanni = Base.classes.altri_danni
ParametriSuolo = Base.classes.parametri_suolo
