-- ho messo select su attributi non chiave in modo che possiamo inserire indici non banali 
--(mi sembra di ricordare dai lab che gli indici primari sulle chiavi fossero gia presenti aka creati dal db dopo la creazione schema)


--1. Tutte le informazioni sulle persone che hanno id > 2000 o che sono musicisti
    select * from persone where id > 2000 or ruolo = 'Musician'

--POSSIBILE OTTIMIZZAZIONE: un indice hash potrebbe migliorare la ricerca per uguaglianza del ruolo




--2. Tutte le informazioni sulle repliche che hanno nome scientifico=...

    select * from repliche where nome_scientifico_specie='Clematis vitalba'

--POSSIBILE OTTIMIZZAZIONE: indice hash potrebbe migliorare la ricerca per uguaglianza sul nome della specie




--3. id, nome e istituto di riferimento per ogni orto che contiene repliche messe a dimora dopo una determinata data (1-4-2023)

	select o.id, nome, o.istituto
		from repliche r join orti o
		on r.id_orto=o.id
	where data_dimora > '1-4-2023 00:00:00'

--POSSIBILE OTTIMIZZAZIONE: un indice btree ordinato sulla data_dimora potrebbe migliorare la ricerca per intervallo
