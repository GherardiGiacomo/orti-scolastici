from loguru import logger
from sqlalchemy import CursorResult, text

from src.py.connection import conn, session
from src.py.populate import (
    insert_alterazioni_fioritura_fruttificazione,
    insert_altri_danni,
    insert_associazione_sensore,
    insert_biomassa_struttura,
    insert_classe,
    insert_finanziamento,
    insert_gruppo,
    insert_gruppo_controllo,
    insert_istituto,
    insert_orto,
    insert_parametri_suolo,
    insert_partecipante_finanziamento,
    insert_persona,
    insert_replica,
    insert_persona_scuola,
    insert_riferimento_istituto,
    insert_riferimento_scuola,
    insert_rilevazione,
    insert_scuola,
    insert_sensore,
)


def get_tables_sizes(schema_name: str) -> CursorResult[list[tuple[str, int]]]:
    query = """
        SELECT relname AS "table",
            pg_total_relation_size(C.oid) AS "size"
        FROM pg_class C
        LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
        WHERE nspname = :schema_name
            AND C.relkind = 'r'
        ORDER BY pg_total_relation_size(C.oid)
    """
    return conn.execute(text(query).bindparams(schema_name=schema_name))


def get_table_size(table_name: str) -> int:
    query = f"""
        SELECT pg_total_relation_size(C.oid) AS "size"
        FROM pg_class C
        LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
        WHERE nspname = 'orti_scolastici'
                AND C.relkind = 'r'
                AND relname = '{table_name}'
    """  # noqa: S608
    result = session.execute(text(query))
    return result.all()[0][0]


if __name__ == "__main__":
    # le tabelle sono ordinate secondo una logica
    tables = [
        "istituti",
        "scuole",
        "persone",
        "persone_scuola",
        "riferimenti_scuola",
        "riferimenti_istituto",
        "classi",
        "finanziamenti",
        "partecipanti_finanziamento",
        "orti",
        "gruppi",
        "specie",
        "repliche",
        "gruppi_controllo",
        "sensori",
        "associazioni_sensore",
        "rilevazioni",
        "biomassa_struttura",
        "alterazioni_fioritura_fruttificazione",
        "altri_danni",
        "parametri_suolo",
    ]
    logger.info("Checking if tables need more data to reach 80000 bytes")
    for table_name in tables:
        while get_table_size(table_name) < 80 * 1000:
            try:
                insert_name = table_name
                match table_name:
                    case "istituti" | "orti":
                        istituto = insert_istituto()
                        scuola = insert_scuola(istituto)
                        insert_classe(scuola)
                        insert_orto(istituto)
                        insert_name = "istituti, scuola, classe, orto"
                    case "scuole":
                        scuola = insert_scuola()
                        insert_classe(scuola)
                        insert_name = "scuole, classe"
                    case "persone" | "persone_scuola":
                        persona = insert_persona()
                        insert_persona_scuola(persona)
                        insert_name = "persone, persone_scuola"
                    case "riferimenti_scuola":
                        persona = insert_persona()
                        insert_riferimento_scuola(persona)
                    case "riferimenti_istituto":
                        persona = insert_persona()
                        insert_riferimento_istituto(persona)
                    case "classi":
                        insert_classe()
                    case "finanziamenti":
                        insert_finanziamento()
                    case "partecipanti_finanziamento":
                        insert_partecipante_finanziamento()
                    case "gruppi":
                        insert_gruppo()
                    case "gruppi_controllo":
                        insert_gruppo_controllo()
                    case "specie":
                        # all specie all already inserted (81920 bytes)
                        pass
                    case "repliche":
                        insert_replica()
                    case "sensori":
                        sensore = insert_sensore()
                        insert_associazione_sensore(sensore)
                        insert_name = "sensori, associazioni_sensore"
                    case "associazioni_sensore":
                        insert_associazione_sensore()
                    case "rilevazioni":
                        insert_rilevazione()
                        insert_biomassa_struttura()
                        insert_alterazioni_fioritura_fruttificazione()
                        insert_altri_danni()
                        insert_parametri_suolo()
                        insert_name = (
                            "rilevazioni, biomassa_struttura, "
                            "alterazioni_fioritura_fruttificazione, "
                            "altri_danni, parametri_suolo"
                        )
                    case "biomassa_struttura":
                        insert_biomassa_struttura()
                    case "alterazioni_fioritura_fruttificazione":
                        insert_alterazioni_fioritura_fruttificazione()
                    case "altri_danni":
                        insert_altri_danni()
                    case "parametri_suolo":
                        insert_parametri_suolo()
                    case _:
                        error_msg = f"Table {table_name} not handled"
                        raise ValueError(error_msg)  # noqa: TRY301
                session.commit()
            except ValueError:
                raise
            except Exception as e:  # noqa: BLE001
                # logger.exception(e)
                session.rollback()
            else:
                logger.info(f"Added a tuple to {insert_name}")
    logger.info("Check completed.")
    for table_name, size in get_tables_sizes("orti_scolastici"):
        logger.info(f"{table_name}: {size} bytes")
    session.close()
    conn.close()
