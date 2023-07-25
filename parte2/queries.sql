set search_path to "orti_scolastici";

-- B. La definizione di una vista che fornisca alcune informazioni riassuntive per ogni attività di biomonitoraggio: per
-- ogni gruppo e per il corrispondente gruppo di controllo mostrare il numero di piante, la specie, l’orto in cui è
-- posizionato il gruppo e, su base mensile, il valore medio dei parametri ambientali e di crescita delle piante (se-
-- lezionare almeno tre parametri, quelli che si ritengono più significativi).

create or replace view vista_parametri_biomonitoraggio as
   select extract(month from ril1.data_rilevazione) as mese,
        g.controllato as gruppo_controllato, g.controllore as gruppo_controllore,
        r1.nome_scientifico_specie as specie_controllata,  r2.nome_scientifico_specie as specie_controllore,
        g1.dislocato as orto_g_controllato, g2.dislocato as orto_g_controllore,
        count(r2.id) as num_repliche_controllore, avg (ps.umidita) as umidita_controllore, avg (ps.temperatura) as temperatura_controllore,
        count(r1.id) as num_repliche_controllato, avg (bs.altezza_pianta) as altezza_pianta_controllata, avg (bs.larghezza_chioma) as larghezza_chioma_controllata
    from gruppi_controllo g
        join repliche r1 on g.controllato = r1.id_gruppo
        join gruppi g1 on g1.id=g.controllore
        join rilevazioni ril1 on ril1.id_replica=r1.id
        join biomassa_struttura bs on bs.id_rilevazione = ril1.id

        join repliche r2 on g.controllore = r2.id_gruppo
        join gruppi g2 on g2.id=g.controllore
        join rilevazioni ril2 on ril2.id_replica=r2.id
        join parametri_suolo ps on ps.id_rilevazione = ril2.id
    where extract(year from ril1.data_rilevazione) = extract(year from CURRENT_DATE) and
        extract(year from ril2.data_rilevazione) = extract(year from CURRENT_DATE) 
        and	extract(month from ril1.data_rilevazione) = extract(month from ril2.data_rilevazione)
    group by gruppo_controllato, specie_controllata, 
            orto_g_controllato,gruppo_controllore,
            specie_controllore,orto_g_controllore, mese
	order by mese;


-- C.a. determinare le scuole che, pur avendo un finanziamento per il progetto, non hanno inserito rilevazioni in questo anno scolastico;
-- per come abbiamo strutturato il database (data l'ambiguità di scuola nella traccia) il finanziamento è relativo all'istituto


select codice_meccanografico_istituto 
    from finanziamenti
where codice_meccanografico_istituto 
    not in (select o.istituto 
    from rilevazioni r 
        join repliche re on r.id_replica=re.id
        join orti o on o.id=re.id_orto
    where (extract(year from r.data_rilevazione)=(extract(year from CURRENT_DATE)-1)
        and extract(month from r.data_rilevazione)>8)
        or 
        (extract(year from r.data_rilevazione)=extract(year from CURRENT_DATE)
        and extract(month from r.data_rilevazione)<7)
        );


-- C.b. determinare le specie utilizzate in tutti i comuni in cui ci sono scuole aderenti al progetto
select r.nome_scientifico_specie
from repliche r
    join gruppi g on g.id = r.id_gruppo
    join orti o on g.dislocato = o.id
    join istituti i on o.istituto = i.codice_meccanografico
group by r.nome_scientifico_specie
having count (distinct i.comune)= (select count(distinct comune)
                from istituti);


-- C.c. determinare per ogni scuola l’individuo/la classe della scuola che ha effettuato più rilevazioni.
select o1.istituto, r1.resp_ril_classe, r1.resp_ril_persona, count(r1.id)
from rilevazioni r1
join repliche re1 on re1.id=r1.id_replica
join gruppi g1 on re1.id_gruppo = g1.id
join orti o1 on g1.dislocato = o1.id
group by o1.istituto, r1.resp_ril_classe, r1.resp_ril_persona
having count(r1.id) = (select max(num_rilevazioni)
                        from (select o2.istituto, r2.resp_ril_classe, r2.resp_ril_persona, count (r2.id) as num_rilevazioni
                            from rilevazioni r2
                            join repliche re2 on re2.id=r2.id_replica
                            join gruppi g2 on re2.id_gruppo = g2.id
                            join orti o2 on g2.dislocato = o2.id
                            group by o2.istituto, r2.resp_ril_classe, r2.resp_ril_persona) as ril_per_resp
                    where o1.istituto = ril_per_resp.istituto
                    )
order by o1.istituto;


-- D.b. funzione che corrisponde alla seguente query parametrica:
-- data una replica con finalità di fitobonifica e due date,
-- determina i valori medi dei parametri rilevati per tale replica nel periodo compreso tra le due date

create or replace function calcola_valori_medi(
    id_replica int,
    data_inizio timestamp,
    data_fine timestamp
)
returns table (
    media_larghezza_chioma decimal,
    media_lunghezza_chioma decimal,
    media_peso_fresco_chioma decimal,
    media_peso_secco_chioma decimal,
    media_altezza_pianta decimal,
    media_lunghezza_radice decimal,
    media_n_frutti decimal
    media_n_fiori decimal
    media_peso_fresco_radici decimal,
    media_peso_secco_radici decimal,
    media_n_foglie_danneggiate decimal
    media_perc_sup_danneggiata_foglia decimal
    media_ph decimal,
    media_umidita decimal,
    media_temperatura decimal
)
as $$
begin
    return QUERY
    select AVG(bs.larghezza_chioma) as media_larghezza_chioma,
           AVG(bs.lunghezza_chioma) as media_lunghezza_chioma,
           AVG(bs.peso_fresco_chioma) as media_peso_fresco_chioma,
           AVG(bs.peso_secco_chioma) as media_peso_secco_chioma,
           AVG(bs.altezza_pianta) as media_altezza_pianta,
           AVG(bs.lunghezza_radice) as media_lunghezza_radice,
           AVG(aff.n_frutti) as media_n_frutti,
           AVG(aff.n_fiori) as media_n_fiori,
           AVG(aff.peso_fresco_radici) as media_peso_fresco_radici,
           AVG(aff.peso_secco_radici) as media_peso_secco_radici,
           AVG(ad.n_foglie_danneggiate) as media_n_foglie_danneggiate,
           AVG(ad.perc_sup_danneggiata_foglia) as media_perc_sup_danneggiata_foglia,
           AVG(ps.ph) as media_ph,
           AVG(ps.umidita) as media_umidita,
           AVG(ps.temperatura) as media_temperatura
    from rilevazioni r
    left join biomassa_struttura bs on bs.id_rilevazione = r.id
    left join alterazioni_fioritura_fruttificazione aff on aff.id_rilevazione = r.id
    left join altri_danni ad on ad.id_rilevazione = r.id
    left join parametri_suolo ps on ps.id_rilevazione = r.id
    where r.id_replica = calcola_valori_medi.id_replica
      and r.data_rilevazione >= data_inizio
      and r.data_rilevazione <= data_fine;
end;
$$ language plpgsql;


-- E.a verifica del vincolo che ogni scuola deovrebbe concentrarsi su tre specie e ogni gruppo dovrebbe contenere 20 repliche

create or replace function verifica_vincolo_scuole()
    returns trigger as $$
declare 
    var_specie_non_nuova int;
begin

    -- conto il numero di specie diverse (nel trigger dopo l'inserimento)
    select count(r.nome_scientifico_specie)
    into strict var_specie_non_nuova
    from repliche r 
    join classi cl
    on r.id_classe=cl.id
    where cl.id_scuola = (select distinct classi.id_scuola
                        from repliche 
                        join classi
                        on repliche.id_classe=classi.id
                        where repliche.id_classe=new.id_classe
                        );

    --se sono più di tre non posso aggiungere nuove specie
    if var_specie_non_nuova > 3 then
        raise exception 'Vincolo violato: la scuola deve concentrarsi su massimo 3 specie';
    end if;
    return new;
end;	
$$ language plpgsql;

create trigger trigger_scuole
after insert or update on repliche
for each row
execute function verifica_vincolo_scuole();


create or replace function verifica_vincolo_gruppi()
    RETURNS TRIGGER AS $$
DECLARE
    var_num_repliche INT;
BEGIN

--conto il numero di repliche diverse da quella che sto inserendo
    select count(r.id)
    into strict var_num_repliche
    from repliche r
    where r.id_gruppo = new.id_gruppo;

--se sono più di 20 non posso aggiungere nuove repliche
    if var_num_repliche > 20 then
        raise exception 'Vincolo violato: ogni gruppo deve contenere al massimo 20 repliche';
    end if;

    return new;
end;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_gruppi
AFTER INSERT OR UPDATE ON repliche
FOR EACH ROW
EXECUTE FUNCTION verifica_vincolo_gruppi();


-- E.b. generazione di un messaggio (o inserimento di una informazione di warning in qualche tabella) quando viene rilevato un valore decrescente per un parametro di biomassa.


CREATE OR REPLACE FUNCTION verifica_decremento_biomassa() RETURNS TRIGGER AS $$
DECLARE
    last_massa RECORD;
BEGIN
    SELECT * INTO last_massa
    FROM biomassa_struttura b
    JOIN rilevazioni r ON
r.id
 = b.id_rilevazione
    WHERE r.id_replica = (
        SELECT r2.id_replica
        FROM rilevazioni r2
        WHERE NEW.id_rilevazione =
r2.id

    )
    ORDER BY data_rilevazione DESC
    LIMIT 1;

    IF last_massa IS NOT NULL OR NEW.peso_fresco_chioma < last_massa.peso_fresco_chioma THEN
        RAISE EXCEPTION 'Il peso è diminuito rispetto all ultima rilevazione';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER verifica_decremento_biomassa_trigger
BEFORE INSERT OR UPDATE ON biomassa_struttura
FOR EACH ROW EXECUTE PROCEDURE verifica_decremento_biomassa();

