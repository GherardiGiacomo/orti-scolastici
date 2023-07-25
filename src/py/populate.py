import random
from datetime import datetime, timedelta
from string import ascii_uppercase, digits

import pytz
from faker import Faker
from loguru import logger
from sqlalchemy import and_, func, or_

from src.py.connection import session
from src.py.custom_data.funding_types import funding_types
from src.py.custom_data.italian_municipalities import municipalities
from src.py.custom_data.italian_streets import streets
from src.py.custom_data.plants import plants
from src.py.custom_data.schools import schools
from src.py.custom_data.sensors import sensors
from src.py.models import (
    AlterazioniFiorituraFruttificazione,
    AltriDanni,
    AssociazioniSensore,
    BiomassaStruttura,
    Classi,
    Finanziamenti,
    Gruppi,
    GruppiControllo,
    Istituti,
    Orti,
    ParametriSuolo,
    PartecipantiFinanziamento,
    Persone,
    Repliche,
    PersoneScuola,
    Rilevazioni,
    Scuole,
    Sensori,
    Specie,
    RiferimentiScuola,
    RiferimentiIstituto,
)

fake = Faker("it_IT")

TOTAL_ISTITUTI = 10


def insert_istituto() -> Istituti:
    while True:
        codice_meccanografico = fake.pystr_format(
            string_format="??????????",
            letters=ascii_uppercase + digits,
        )
        if (
            session.query(Istituti.codice_meccanografico)
            .filter_by(codice_meccanografico=codice_meccanografico)
            .all()
        ):
            continue
        nome = fake.company()
        via = random.choice(streets)
        cap = fake.random_number(digits=5, fix_len=True)
        comune, provincia = random.choice(municipalities)
        istituto = Istituti(
            codice_meccanografico=codice_meccanografico,
            nome=nome,
            via=via,
            cap=cap,
            comune=comune,
            provincia=provincia,
        )
        session.add(istituto)
        # siccome un istituto ha almeno una scuola e un orto li creo e li aggiungo
        # scuola = insert_scuola(istituto)
        # insert_classe(scuola)
        # insert_orto(istituto)
        return istituto


def insert_scuola(istituto: Istituti | None = None) -> Scuole:
    while True:
        if not istituto:
            istituti = session.query(Istituti).all()
            if istituti:
                istituto = random.choice(istituti)
            else:
                istituto = insert_istituto()
                logger.info("Added a new institute to be used for a school")
        tipo, ciclo = random.choice(schools)
        scuola = Scuole(
            tipo=tipo,
            ciclo=ciclo,
            codice_meccanografico=istituto.codice_meccanografico,
        )
        if (
            session.query(Scuole)
            .filter_by(
                tipo=tipo,
                ciclo=ciclo,
                codice_meccanografico=istituto.codice_meccanografico,
            )
            .all()
        ):
            continue
        session.add(scuola)
        session.flush()
        return scuola


def insert_persona() -> Persone:
    nome = fake.first_name()
    cognome = fake.last_name()
    email = fake.email()
    ruolo = fake.job()
    telefono = fake.msisdn()
    persona = Persone(
        nome=nome,
        cognome=cognome,
        email=email,
        ruolo=ruolo,
        telefono=telefono,
    )
    session.add(persona)
    session.flush()
    return persona


def insert_persona_scuola(
    persona: Persone,
    scuola: Scuole | None = None,
) -> PersoneScuola:
    if scuola is None:
        scuole = session.query(Scuole).all()
        if scuole:
            scuola = random.choice(scuole)
        else:
            scuola = insert_scuola()
            logger.info("Added a new school to be used for a reference")
    persona_scuola = PersoneScuola(id_scuola=scuola.id, id_persona=persona.id)
    session.add(persona_scuola)
    return persona_scuola


def insert_riferimento_scuola(
    persona: Persone,
    scuola: Scuole | None = None,
) -> RiferimentiScuola:
    if scuola is None:
        scuole = session.query(Scuole).all()
        if scuole:
            scuola = random.choice(scuole)
        else:
            scuola = insert_scuola()
            logger.info("Added a new school to be used for a reference")
    riferimento_scuola = RiferimentiScuola(id_scuola=scuola.id, id_persona=persona.id)
    session.add(riferimento_scuola)
    return riferimento_scuola


def insert_riferimento_istituto(
    persona: Persone,
    istituto: Istituti | None = None,
) -> RiferimentiIstituto:
    if istituto is None:
        istituti = session.query(Istituti).all()
        if istituti:
            istituto = random.choice(istituti)
        else:
            istituto = insert_istituto()
            logger.info("Added a new school to be used for a reference")
    riferimento_istituto = RiferimentiIstituto(codice_meccanografico=istituto.codice_meccanografico, id_persona=persona.id)
    session.add(riferimento_istituto)
    return riferimento_istituto


def insert_classe(scuola: Scuole | None = None) -> Classi:
    while True:
        if scuola is None:
            scuole = session.query(Scuole).all()
            if scuole:
                scuola = random.choice(scuole)
            else:
                scuola = insert_scuola()
                logger.info("Added a new school to be used for a class")
        nome = f"{random.randint(1, 5)}{fake.random_letter().upper()}"
        docenti_riferimento = (
            session.query(PersoneScuola.id_persona)
            .filter_by(id_scuola=scuola.id)
            .all()
        )
        if docenti_riferimento:
            docente_riferimento = random.choice(docenti_riferimento)[0]
        else:
            docente_riferimento = insert_persona_scuola(
                insert_persona(),
                scuola,
            ).id_persona
            logger.info("Added a new person to be the head of the class")

        classe = Classi(
            nome=nome,
            id_scuola=scuola.id,
            docente_riferimento=docente_riferimento,
        )
        if (
            session.query(Classi)
            .filter_by(
                nome=nome,
                id_scuola=scuola.id,
            )
            .all()
        ):
            continue
        session.add(classe)
        session.flush()
        return classe


def insert_finanziamento(
    istituto: Istituti | None = None,
    capo: Persone | None = None,
) -> Finanziamenti:
    if istituto is None:
        istituti = (
            session.query(Istituti)
            .outerjoin(Finanziamenti)
            .filter(Finanziamenti.codice_meccanografico_istituto.is_(None))
            .all()
        )
        if istituti:
            istituto = random.choice(istituti)
        else:
            istituto = insert_istituto()
            logger.info("Added a new institute to be funded")
    if capo is None:
        persone = session.query(Persone).all()
        if persone:
            capo = random.choice(persone)
        else:
            capo = insert_persona()
            logger.info("Added a new person to be the head of the funding")
    tipo = random.choice(funding_types)
    finanziamento = Finanziamenti(
        codice_meccanografico_istituto=istituto.codice_meccanografico,
        tipo=tipo,
        capo=capo.id,
    )
    session.add(finanziamento)
    session.flush()
    return finanziamento


def get_pair_finanziamento_persona(
    finanziamento: Finanziamenti | None,
) -> tuple[Finanziamenti, Persone]:
    if finanziamento is None:
        finanziamenti = session.query(Finanziamenti).all()
        if finanziamenti:
            finanziamento = random.choice(finanziamenti)
        else:
            finanziamento = insert_finanziamento()
            logger.info("Added a new funding to be used")
    # prendo tutte le persone che non partecipano al finanziamento
    persone = (
        session.query(Persone)
        .filter(
            ~Persone.id.in_(
                session.query(PartecipantiFinanziamento.id_persona).filter_by(
                    finanziamento=finanziamento.codice_meccanografico_istituto,
                ),
            ),
        )
        .all()
    )
    if persone:
        return finanziamento, random.choice(persone)
    persona = insert_persona()
    logger.info("Added a new person to be part of the funding")
    return finanziamento, persona


def insert_partecipante_finanziamento(
    finanziamento: Finanziamenti | None = None,
    persona: Persone | None = None,
) -> PartecipantiFinanziamento:
    if finanziamento is None or persona is None:
        finanziamento, persona = get_pair_finanziamento_persona(finanziamento)
    partecipante_finanziamento = PartecipantiFinanziamento(
        finanziamento=finanziamento.codice_meccanografico_istituto,
        id_persona=persona.id,
    )
    session.add(partecipante_finanziamento)
    return partecipante_finanziamento


def insert_orto(istituto: Istituti) -> Orti:
    while True:
        nome = fake.company()
        tipo = bool(random.getrandbits(1))
        superficie_m2 = random.randint(1, 1000)
        latitudine = round(random.uniform(-90, 90), 6)
        longitudine = round(random.uniform(-180, 180), 6)
        ok_controllo = bool(random.getrandbits(1))
        orto = Orti(
            istituto=istituto.codice_meccanografico,
            nome=nome,
            tipo=tipo,
            superficie_m2=superficie_m2,
            latitudine=latitudine,
            longitudine=longitudine,
            ok_controllo=ok_controllo,
        )
        if (
            session.query(Orti)
            .filter_by(
                istituto=istituto.codice_meccanografico,
                nome=nome,
            )
            .all()
        ):
            continue
        session.add(orto)
        session.flush()
        return orto


def insert_gruppo(orto: Orti | None = None, ok_controllo: bool | None = None) -> Gruppi:
    if orto is None:
        orti = session.query(Orti).all()
        if orti:
            orto = random.choice(orti)
        else:
            istituto = insert_istituto()
            logger.info("Added a new institute to be used for a garden")
            orto = insert_orto(istituto)
            logger.info("Added a new garden to be used for a group")
    if ok_controllo is None:
        ok_controllo = bool(random.getrandbits(1))
    gruppo = Gruppi(ok_controllo=ok_controllo, dislocato=orto.id)
    session.add(gruppo)
    session.flush()
    return gruppo


def insert_gruppo_controllo(controllore: Gruppi | None = None) -> GruppiControllo:
    if controllore is None:
        # prendo un gruppo da usare come controllore che non è controllato
        controllori = (
            session.query(Gruppi)
            .filter(
                and_(
                    Gruppi.ok_controllo == True,  # noqa: E712,
                    ~Gruppi.id.in_(
                        session.query(GruppiControllo.controllato).scalar_subquery(),
                    ),
                ),
            )
            .all()
        )

        if controllori:
            controllore = random.choice(controllori)
        else:
            controllore = insert_gruppo(ok_controllo=True)

    # prendo tutti i gruppi che possono essere controllati,
    # non è il controllore scelto
    # non sono controllori,
    # non sono controllati
    # il totale delle repliche associate a controllore deve essere uguale
    # al totale delle repliche associate a controllato
    totale_repliche_controllore = (
        session.query(func.count(Repliche.id))
        .filter(
            Repliche.id_gruppo == controllore.id,
        )
        .scalar()
    )

    controllati = (
        session.query(Gruppi)
        .join(Repliche, Gruppi.id == Repliche.id_gruppo)
        .filter(
            and_(
                Gruppi.ok_controllo == True,  # noqa: E712
                Gruppi.id != controllore.id,
                ~(
                    Gruppi.id.in_(
                        session.query(GruppiControllo.controllore).scalar_subquery(),
                    )
                ),
                ~(
                    Gruppi.id.in_(
                        session.query(GruppiControllo.controllato).scalar_subquery(),
                    )
                ),
            ),
        )
        .group_by(Gruppi.id)
        .having(func.count(Repliche.id) == totale_repliche_controllore)
        .all()
    )

    if controllati:
        controllato = random.choice(controllati)
    else:
        controllato = insert_gruppo(ok_controllo=True)
        logger.info("Added a new group to be controlled")

    gruppo_controllo = GruppiControllo(
        controllore=controllore.id,
        controllato=controllato.id,
    )
    session.add(gruppo_controllo)
    return gruppo_controllo


def insert_specie(
    nome_scientifico: str,
    nome_comune: str,
    esposizione: int | None = None,
) -> Specie:
    if esposizione is None:
        esposizione = random.randint(0, 1440)
    specie = Specie(
        nome_scientifico=nome_scientifico,
        nome_comune=nome_comune,
        esposizione=esposizione,
    )
    session.add(specie)
    return specie


def insert_replica(
    specie: Specie | None = None,
    gruppo: Gruppi | None = None,
    classe: Classi | None = None,
) -> Repliche:
    if gruppo is None:
        # prendo i gruppi che hanno meno di 20 repliche
        gruppi = (
            session.query(Gruppi)
            .outerjoin(Repliche, Gruppi.id == Repliche.id_gruppo)
            .group_by(Gruppi.id)
            .having(func.count(Repliche.id) < 20)
            .all()
        )
        if gruppi:
            gruppo = random.choice(gruppi)
        else:
            orto = None
            if classe:
                orto = (
                    session.query(Orti)
                    .join(Scuole, Orti.istituto == Scuole.codice_meccanografico)
                    .join(Classi, Scuole.id == Classi.id_scuola)
                    .filter(Classi.id == classe.id)
                    .first()
                )
            gruppo = insert_gruppo(orto)
            logger.info("Added a new group to be used for a replica")
    # se specie è None per come è stata progettata la populate significa
    # che ci sono già delle repliche inserite
    if specie is None:
        # prendo le possibili specie che possono inserire
        # perchè ogni istituto si deve concentrare su massimo 3 specie diverse
        specie_istituto = (
            session.query(Specie)
            .join(
                Repliche,
                Specie.nome_scientifico == Repliche.nome_scientifico_specie,
            )
            .join(
                Gruppi,
                Repliche.id_gruppo == Gruppi.id,
            )
            .join(
                Orti,
                Gruppi.dislocato == Orti.id,
            )
            .join(
                Istituti,
                Orti.istituto == Istituti.codice_meccanografico,
            )
            .filter(
                Orti.id == gruppo.dislocato,
            )
            .all()
        )
        if len(specie_istituto) < 3:
            specie = session.query(Specie).all()
            specie_istituto += random.sample(specie, 3 - len(specie_istituto))
        specie = random.choice(specie_istituto)
    if classe is None:
        # prendo le possibili classi che possono inserire una replica
        # in quel gruppo, per quell'orto, per quell'istituto
        classi = (
            session.query(Classi)
            .join(Scuole, Classi.id_scuola == Scuole.id)
            .join(
                Istituti,
                Scuole.codice_meccanografico == Istituti.codice_meccanografico,
            )
            .join(Orti, Istituti.codice_meccanografico == Orti.istituto)
            .filter(Orti.id == gruppo.dislocato)
            .all()
        )

        classe = random.choice(classi)

    scopo = bool(random.getrandbits(1))
    now = datetime.now(tz=pytz.timezone("CET"))
    start_date = now - timedelta(days=365 * 2)
    random_timestamp = start_date + (now - start_date) * random.random()
    data_dimora = random_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    replica = Repliche(
        scopo=scopo,
        data_dimora=data_dimora,
        nome_scientifico_specie=specie.nome_scientifico,
        id_gruppo=gruppo.id,
        id_orto=gruppo.dislocato,
        id_classe=classe.id,
    )
    session.add(replica)
    session.flush()
    return replica


def insert_sensore(orto: Orti | None = None, tipo: str | None = None) -> Sensori:
    while True:
        if tipo is None:
            tipo = random.choice(sensors)
        if orto is None:
            orto = random.choice(session.query(Orti).all())
        seriale = "".join(random.choices(ascii_uppercase + digits, k=32))
        if (
            session.query(Sensori)
            .filter_by(
                seriale=seriale,
            )
            .all()
        ):
            continue
        sensore = Sensori(seriale=seriale, tipo=tipo, id_orto=orto.id)
        session.add(sensore)
        return sensore


def insert_associazione_sensore(sensore: Sensori | None = None) -> AssociazioniSensore:
    if sensore is None:
        # get all sensors that are not assigned to all replicas

        sensore = random.choice(
            session.query(Sensori).filter(Sensori.tipo != "Arduino").all(),
        )
    # prendo tutte le repliche che hanno in comune l'orto dove è associato il sensore
    # e che non hanno già quel sensore associato
    repliche = (
        session.query(Repliche)
        .join(Orti, Repliche.id_orto == Orti.id)
        .join(Sensori, Orti.id == Sensori.id_orto)
        .outerjoin(AssociazioniSensore, AssociazioniSensore.id_replica == Repliche.id)
        .filter(
            and_(
                Orti.id == sensore.id_orto,
                Sensori.tipo != "Arduino",
                or_(
                    AssociazioniSensore.seriale != sensore.seriale,
                    AssociazioniSensore.seriale.is_(None),
                ),
            ),
        )
        .all()
    )
    if repliche:
        replica = random.choice(repliche)
    else:
        # prendo i gruppi che hanno meno di 20 repliche
        # e appartengo all'orto del sensore
        gruppi = (
            session.query(Gruppi)
            .join(Orti, Gruppi.dislocato == Orti.id)
            .outerjoin(Repliche, Gruppi.id == Repliche.id_gruppo)
            .filter(Orti.id == sensore.id_orto)
            .group_by(Gruppi.id)
            .having(func.count(Repliche.id) < 20)
            .all()
        )
        if gruppi:
            gruppo = random.choice(gruppi)
        else:
            gruppo = insert_gruppo(
                session.query(Orti).filter_by(id=sensore.id_orto).first(),
            )
            logger.info("Added a new group to be used for a replica")
        replica = insert_replica(gruppo=gruppo)
        logger.info("Added a new replica to be used for a sensor association")
    associazione_sensore = AssociazioniSensore(
        seriale=sensore.seriale,
        id_replica=replica.id,
    )
    session.add(associazione_sensore)
    return associazione_sensore


def insert_rilevazione(replica: Repliche | None = None) -> Rilevazioni:
    if replica is None:
        repliche = session.query(Repliche).all()
        if repliche:
            replica = random.choice(repliche)
        else:
            replica = insert_replica()
            logger.info("Added a new replica to be used for a reading")
    classi = (
        session.query(Classi)
        .filter(
            and_(
                Classi.id_scuola == Scuole.id,
                Scuole.codice_meccanografico == Orti.istituto,
                Orti.id == replica.id_orto,
            ),
        )
        .all()
    )
    # do the same but with join
    # ? qua si passa per forza per riferimenti
    persone = (
        session.query(Persone)
        .filter(
            and_(
                Persone.id == PersoneScuola.id_persona,
                PersoneScuola.id_scuola == Scuole.id,
                Scuole.codice_meccanografico == Orti.istituto,
                Orti.id == replica.id_orto,
            ),
        )
        .all()
    )
    # ? da sistemare le due query sopra
    resp_ins_classe = None
    resp_ins_persona = None
    resp_ril_classe = None
    resp_ril_persona = None
    if random.randint(0, 1):
        resp_ins_classe = random.choice(classi).id
    else:
        resp_ins_persona = random.choice(persone).id
    if random.randint(0, 1):
        resp_ril_classe = random.choice(classi).id
    else:
        resp_ril_persona = random.choice(persone).id
    data_dimora = replica.data_dimora
    if isinstance(data_dimora, str):
        data_dimora = datetime.strptime(data_dimora, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=pytz.timezone("CET"),
        )
    data_rilevazione = (
        data_dimora
        + timedelta(days=random.randint(0, 182))
        + timedelta(hours=random.randint(0, 23))
        + timedelta(minutes=random.randint(0, 59))
    )
    data_inserimento = (
        data_rilevazione
        + timedelta(hours=random.randint(0, 23))
        + timedelta(minutes=random.randint(0, 59))
    )
    rilevazione = Rilevazioni(
        data_inserimento=data_inserimento,
        data_rilevazione=data_rilevazione,
        id_replica=replica.id,
        resp_ins_classe=resp_ins_classe,
        resp_ril_classe=resp_ril_classe,
        resp_ins_persona=resp_ins_persona,
        resp_ril_persona=resp_ril_persona,
    )
    session.add(rilevazione)
    session.flush()
    return rilevazione


def insert_biomassa_struttura(
    rilevazione: Rilevazioni | None = None,
) -> BiomassaStruttura:
    if rilevazione is None:
        rilevazioni = (
            session.query(Rilevazioni)
            .outerjoin(BiomassaStruttura)
            .filter(
                BiomassaStruttura.id_rilevazione.is_(None),
            )
            .all()
        )
        if rilevazioni:
            rilevazione = random.choice(rilevazioni)
        else:
            rilevazione = insert_rilevazione()
    larghezza_chioma = random.randint(0, 1000)
    lunghezza_chioma = random.randint(0, 1000)
    peso_fresco_chioma = random.randint(0, 1000)
    peso_secco_chioma = random.randint(0, 1000)
    altezza_pianta = random.randint(0, 10000)
    lunghezza_radice = random.randint(0, 10000)
    biomassa_struttura = BiomassaStruttura(
        id_rilevazione=rilevazione.id,
        larghezza_chioma=larghezza_chioma,
        lunghezza_chioma=lunghezza_chioma,
        peso_fresco_chioma=peso_fresco_chioma,
        peso_secco_chioma=peso_secco_chioma,
        altezza_pianta=altezza_pianta,
        lunghezza_radice=lunghezza_radice,
    )
    session.add(biomassa_struttura)
    return biomassa_struttura


def insert_alterazioni_fioritura_fruttificazione(
    rilevazione: Rilevazioni | None = None,
) -> AlterazioniFiorituraFruttificazione:
    if rilevazione is None:
        rilevazioni = (
            session.query(Rilevazioni)
            .outerjoin(AlterazioniFiorituraFruttificazione)
            .filter(
                AlterazioniFiorituraFruttificazione.id_rilevazione.is_(None),
            )
            .all()
        )
        if rilevazioni:
            rilevazione = random.choice(rilevazioni)
        else:
            rilevazione = insert_rilevazione()
    n_frutti = random.randint(0, 1000)
    n_fiori = random.randint(0, 1000)
    peso_fresco_radici = random.randint(0, 10000)
    peso_secco_radici = random.randint(0, 10000)
    alterazioni_fioritura_fruttificazione = AlterazioniFiorituraFruttificazione(
        id_rilevazione=rilevazione.id,
        n_frutti=n_frutti,
        n_fiori=n_fiori,
        peso_fresco_radici=peso_fresco_radici,
        peso_secco_radici=peso_secco_radici,
    )
    session.add(alterazioni_fioritura_fruttificazione)
    return alterazioni_fioritura_fruttificazione


def insert_altri_danni(rilevazione: Rilevazioni | None = None) -> AltriDanni:
    if rilevazione is None:
        rilevazioni = (
            session.query(Rilevazioni)
            .outerjoin(AltriDanni)
            .filter(
                AltriDanni.id_rilevazione.is_(None),
            )
            .all()
        )
        if rilevazioni:
            rilevazione = random.choice(rilevazioni)
        else:
            rilevazione = insert_rilevazione()
    n_foglie_danneggiate = random.randint(0, 1000)
    perc_sup_danneggiata_foglia = random.randint(0, 100)
    altri_danni = AltriDanni(
        id_rilevazione=rilevazione.id,
        n_foglie_danneggiate=n_foglie_danneggiate,
        perc_sup_danneggiata_foglia=perc_sup_danneggiata_foglia,
    )
    session.add(altri_danni)
    return altri_danni


def insert_parametri_suolo(rilevazione: Rilevazioni | None = None) -> ParametriSuolo:
    if rilevazione is None:
        rilevazioni = (
            session.query(Rilevazioni)
            .outerjoin(ParametriSuolo)
            .filter(
                ParametriSuolo.id_rilevazione.is_(None),
            )
            .all()
        )
        if rilevazioni:
            rilevazione = random.choice(rilevazioni)
        else:
            rilevazione = insert_rilevazione()
    ph = round(random.uniform(0, 14), 1)
    umidita = round(random.uniform(0, 100), 2)
    temperatura = round(random.uniform(-10, 50), 1)
    parametri_suolo = ParametriSuolo(
        id_rilevazione=rilevazione.id,
        ph=ph,
        umidita=umidita,
        temperatura=temperatura,
    )
    session.add(parametri_suolo)
    return parametri_suolo


if __name__ == "__main__":
    try:
        # istituti
        istituti: list[Istituti] = [insert_istituto() for _ in range(TOTAL_ISTITUTI)]
        assert len(istituti) == len(session.query(Istituti).all())
        logger.info(f"Inserted {len(istituti)} istituti.")

        # aggiungo almeno una scuola per istituto (max 3)
        scuole: list[Scuole] = []
        for istituto in istituti:
            scuole += [insert_scuola(istituto) for _ in range(random.randint(1, 3))]
        assert len(scuole) == len(session.query(Scuole).all())
        logger.info(f"Inserted {len(scuole)} scuole.")

        # riferimenti scuola e persone
        persone_scuola: list[PersoneScuola] = []
        persone: list[Persone] = []
        for scuola in scuole:
            # aggiungo almeno una persona per scuola (max 10)
            for _ in range(random.randint(1, 10)):
                persona = insert_persona()
                persone.append(persona)
                persone_scuola.append(insert_persona_scuola(persona, scuola))

        # aggiungo altre persone a scuole casuali
        for _ in range(len(scuole) * 100):
            persona = insert_persona()
            persone.append(persona)
            persone_scuola.append(
                insert_persona_scuola(persona, random.choice(scuole)),
            )

        assert len(persone) == len(session.query(Persone).all())
        assert len(persone_scuola) == len(session.query(PersoneScuola).all())
        logger.info(f"Inserted {len(persone)} persone.")
        logger.info(f"Inserted {len(persone_scuola)} riferimenti scuola.")


        # aggiungo riferimenti
        riferimenti_scuola: list[RiferimentiScuola] = []
        riferimenti_istituto: list[RiferimentiIstituto] = []
        for _ in range(len(scuole) * 2):
            persona = random.choice(persone)
            riferimenti_scuola.append(insert_riferimento_scuola(persona))
            riferimenti_istituto.append(insert_riferimento_istituto(persona))

        assert len(riferimenti_scuola) == len(session.query(RiferimentiScuola).all())
        assert len(riferimenti_istituto) == len(session.query(RiferimentiIstituto).all())
        logger.info(f"Inserted {len(riferimenti_scuola)} riferimenti scuola.")
        logger.info(f"Inserted {len(riferimenti_istituto)} riferimenti istituto.")

        # classi
        classi: list[Classi] = []
        for scuola in scuole:
            # aggiungo almeno una classe per scuola (max 10)
            classi += [insert_classe(scuola) for _ in range(random.randint(1, 10))]

        assert len(classi) == len(session.query(Classi).all())
        logger.info(f"Inserted {len(classi)} classi.")

        # finanziamenti
        finanziamenti: list[Finanziamenti] = []
        partecipanti_finanziamenti: list[PartecipantiFinanziamento] = []
        for istituto in istituti:
            # 50% di probabilità che l'istituto abbia un finanziamento
            if random.randint(0, 1):
                finanziamento = insert_finanziamento(istituto, random.choice(persone))
                finanziamenti.append(finanziamento)
                # aggiungo almeno un partecipante al finanziamento
                partecipanti_finanziamenti.append(
                    insert_partecipante_finanziamento(
                        finanziamento,
                        random.choice(persone),
                    ),
                )

        assert len(finanziamenti) == len(session.query(Finanziamenti).all())
        logger.info(f"Inserted {len(finanziamenti)} finanziamenti.")

        # partecipanti finanziamento
        partecipanti_finanziamenti += [
            insert_partecipante_finanziamento()
            for _ in range(min(len(finanziamenti) * 50, len(persone)))
        ]

        assert len(partecipanti_finanziamenti) == len(
            session.query(PartecipantiFinanziamento).all(),
        )
        logger.info(
            f"Inserted {len(partecipanti_finanziamenti)} partecipanti finanziamenti.",
        )

        # orti
        orti: list[Orti] = [insert_orto(istituto) for istituto in istituti]

        assert len(orti) == len(session.query(Orti).all())
        logger.info(f"Inserted {len(orti)} orti.")

        # gruppi
        # aggiungo un gruppo per ogni orto
        gruppi: list[Gruppi] = [insert_gruppo(orto) for orto in orti]
        # aggiungo altri gruppi casuali
        gruppi += [insert_gruppo(random.choice(orti)) for _ in range(len(orti) * 10)]
        # aggiungo dei gruppi di biomonitoraggio extra
        gruppi += [insert_gruppo(ok_controllo=True) for _ in range(len(gruppi) // 2)]

        assert len(gruppi) == len(session.query(Gruppi).all())
        logger.info(f"Inserted {len(gruppi)} gruppi.")

        # specie
        specie: list[Specie] = [
            insert_specie(nome_scientifico, nome_comune)
            for nome_scientifico, nome_comune in plants.items()
        ]

        assert len(specie) == len(session.query(Specie).all())
        logger.info(f"Inserted {len(specie)} specie.")

        # repliche
        repliche: list[Repliche] = []

        # 20 repliche per ogni gruppo di ogni istituto con massimo 3 specie distinte
        for istituto in istituti:
            specie_istituto = random.sample(specie, 3)
            gruppi_istituto = (
                session.query(Gruppi)
                .filter(
                    and_(
                        Gruppi.dislocato == Orti.id,
                        Orti.istituto == istituto.codice_meccanografico,
                    ),
                )
                .all()
            )
            for gruppo in gruppi_istituto:
                repliche += [
                    insert_replica(random.choice(specie_istituto), gruppo)
                    for _ in range(20)
                ]

        assert len(repliche) == len(session.query(Repliche).all())
        logger.info(f"Inserted {len(repliche)} repliche.")

        # gruppi controllo
        gruppi_biomonitoraggio = [gruppo for gruppo in gruppi if gruppo.ok_controllo]

        controllori = random.sample(
            gruppi_biomonitoraggio,
            random.randint(1, len(gruppi_biomonitoraggio) // 2 - 1),
        )
        gruppi_controllo: list[GruppiControllo] = [
            insert_gruppo_controllo(controllore) for controllore in controllori
        ]

        assert len(gruppi_controllo) == len(session.query(GruppiControllo).all())
        logger.info(f"Inserted {len(gruppi_controllo)} gruppi controllo.")

        # sensori
        sensori: list[Sensori] = []
        for orto in orti:
            sensori.append(insert_sensore(orto, "Arduino"))
            sensori += [insert_sensore(orto) for _ in range(random.randint(1, 10))]

        assert len(sensori) == len(session.query(Sensori).all())
        logger.info(f"Inserted {len(sensori)} sensori.")

        # associazioni sensore
        sensori_rilevazioni = [
            sensore for sensore in sensori if sensore.tipo != "Arduino"
        ]
        associazioni_sensori: list[AssociazioniSensore] = [
            insert_associazione_sensore(sensore) for sensore in sensori_rilevazioni
        ]

        assert len(associazioni_sensori) == len(
            session.query(AssociazioniSensore).all(),
        )
        logger.info(f"Inserted {len(associazioni_sensori)} associazioni sensore.")

        # rilevazioni
        rilevazioni = [insert_rilevazione() for _ in range(1000)]

        assert len(rilevazioni) == len(session.query(Rilevazioni).all())
        logger.info(f"Inserted {len(rilevazioni)} rilevazioni.")

        # biomassa_struttura
        # alterazioni_fioritura_fruttificazione
        # altri_danni
        # parametri_suolo
        biomassa_strutture: list[BiomassaStruttura] = []
        alterazioni_fioritura_fruttificazioni: list[
            AlterazioniFiorituraFruttificazione
        ] = []
        altri_danni: list[AltriDanni] = []
        parametri_suolo: list[ParametriSuolo] = []
        for rilevazione in rilevazioni:
            biomassa_strutture.append(insert_biomassa_struttura(rilevazione))
            alterazioni_fioritura_fruttificazioni.append(
                insert_alterazioni_fioritura_fruttificazione(rilevazione),
            )
            altri_danni.append(insert_altri_danni(rilevazione))
            parametri_suolo.append(insert_parametri_suolo(rilevazione))

        assert len(biomassa_strutture) == len(session.query(BiomassaStruttura).all())
        logger.info(f"Inserted {len(biomassa_strutture)} biomassa_strutture.")

        assert len(alterazioni_fioritura_fruttificazioni) == len(
            session.query(AlterazioniFiorituraFruttificazione).all(),
        )
        logger.info(
            "Inserted"
            f" {len(alterazioni_fioritura_fruttificazioni)}"
            " alterazioni_fioritura_fruttificazioni.",
        )

        assert len(altri_danni) == len(session.query(AltriDanni).all())
        logger.info(f"Inserted {len(altri_danni)} altri_danni.")

        assert len(parametri_suolo) == len(session.query(ParametriSuolo).all())
        logger.info(f"Inserted {len(parametri_suolo)} parametri_suolo.")

        session.commit()
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        session.rollback()
    else:
        logger.info("Populate completed successfully.")
    finally:
        session.close()
