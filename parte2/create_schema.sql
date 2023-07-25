drop schema if exists orti_scolastici cascade;
create schema orti_scolastici;
set search_path to orti_scolastici;

create table istituti (
	codice_meccanografico char(10) primary key,
	nome varchar(64) not null,
	via varchar(64) not null,
	cap char(5) not null,
	comune varchar(64) not null,
	provincia char(2) not null
);

create table scuole (
	id integer primary key generated always as identity,
	ciclo varchar(32) not null,
	tipo varchar(128) not null,
	codice_meccanografico char(10) not null references istituti(codice_meccanografico) on delete cascade on update cascade,
	unique (tipo, ciclo, codice_meccanografico)
);

create table persone (
	id integer primary key generated always as identity,
	nome varchar(64) not null,
	cognome varchar(64) not null,
	email varchar(256) not null,
	ruolo varchar(64) not null,
	telefono varchar(15)
);

create table persone_scuola (
	id_scuola integer not null references scuole(id) on delete cascade on update cascade,
	id_persona integer not null references persone(id) on delete cascade on update cascade,
	primary key (id_scuola, id_persona),
	foreign key (id_scuola) references scuole(id) on delete cascade on update cascade,
	foreign key (id_persona) references persone(id) on delete cascade on update cascade
);

create table riferimenti_scuola (
	id_scuola integer not null references scuole(id) on delete cascade on update cascade,
	id_persona integer not null references persone(id) on delete cascade on update cascade,
	primary key (id_scuola, id_persona),
	foreign key (id_scuola) references scuole(id) on delete cascade on update cascade,
	foreign key (id_persona) references persone(id) on delete cascade on update cascade
);

create table riferimenti_istituto (
	codice_meccanografico char(10) not null references istituti(codice_meccanografico) on delete cascade on update cascade,
	id_persona integer not null references persone(id) on delete cascade on update cascade,
	primary key (codice_meccanografico, id_persona),
	foreign key (codice_meccanografico) references istituti(codice_meccanografico) on delete cascade on update cascade,
	foreign key (id_persona) references persone(id) on delete cascade on update cascade
);

create table classi (
	id integer primary key generated always as identity,
	nome char(2) not null, -- in formato come 3B\1L\6F
	id_scuola integer not null references scuole(id) on delete cascade on update cascade,
	docente_riferimento integer not null references persone(id) on delete cascade on update cascade,
	unique (nome, id_scuola)
);

create table finanziamenti (
	codice_meccanografico_istituto char(10) primary key references istituti(codice_meccanografico) on delete cascade on update cascade,
	tipo varchar(64) not null,
	capo integer not null references persone(id) on delete cascade on update cascade
);

create table partecipanti_finanziamento (
	id_persona integer not null references persone(id) on delete cascade on update cascade,
	finanziamento char(10) not null references finanziamenti(codice_meccanografico_istituto) on delete cascade on update cascade, -- codice_meccanografico
	primary key (id_persona, finanziamento),
	foreign key (id_persona) references persone(id) on delete cascade on update cascade,
	foreign key (finanziamento) references finanziamenti(codice_meccanografico_istituto) on delete cascade on update cascade
);

create table orti (
	id integer primary key generated always as identity,
	istituto char(10) not null references istituti(codice_meccanografico) on delete cascade on update cascade, -- codice meccanografico
	nome varchar(64) not null,
	tipo bool not null, -- false terra, true vaso
	superficie_m2 integer not null,
	latitudine DECIMAL(9,6) check (latitudine >= -90 and latitudine <= 90),
    longitudine DECIMAL(9,6) check (longitudine >= -180 and longitudine <= 180),
	ok_controllo bool not null,
	unique (istituto, nome)
);

create table gruppi (
	id integer primary key generated always as identity,
	ok_controllo boolean not null, -- true può controllare (ovvero è un gruppo di biomonitoraggio), false fitobonifica
	dislocato integer not null references orti(id) on delete cascade on update cascade
);

create table gruppi_controllo (
	controllore integer not null references gruppi(id) on delete cascade on update cascade,
	controllato integer not null references gruppi(id) on delete cascade on update cascade,
	primary key (controllore, controllato),
	foreign key (controllore) references gruppi(id) on delete cascade on update cascade,
	foreign key (controllato) references gruppi(id) on delete cascade on update cascade
);

create table specie (
	nome_scientifico varchar(64) primary key,
	nome_comune varchar(64) not null,
	esposizione integer not null check (esposizione >= 0 and esposizione <= 1440) -- 24h in minuti
);

create table repliche (
	id integer primary key generated always as identity,
	scopo boolean not null, -- true biomonitoraggio, false fitobonifica
	data_dimora timestamp not null,
	nome_scientifico_specie varchar(64) not null references specie(nome_scientifico) on delete cascade on update cascade,
	id_gruppo integer not null references gruppi(id) on delete cascade on update cascade,
	id_orto integer not null references orti(id) on delete cascade on update cascade,
	id_classe integer not null references classi(id) on delete cascade on update cascade
);

create table sensori (
	seriale char(32) primary key,
	tipo varchar(64) not null,
	id_orto integer not null references orti(id) on delete cascade on update cascade
);

create table associazioni_sensore (
	seriale char(32) references sensori(seriale) on delete cascade on update cascade,
	id_replica integer references repliche(id) on delete cascade on update cascade,
	primary key (seriale, id_replica),
	foreign key (seriale) references sensori(seriale) on delete cascade on update cascade,
	foreign key (id_replica) references repliche(id) on delete cascade on update cascade
);

create table rilevazioni (
	id integer primary key generated always as identity,
	data_inserimento timestamp not null,
	data_rilevazione timestamp not null,
	id_replica integer not null references repliche(id) on delete cascade on update cascade,
	resp_ins_classe integer references classi(id) on delete cascade on update cascade,
	resp_ril_classe integer references classi(id) on delete cascade on update cascade,
	resp_ins_persona integer references persone(id) on delete cascade on update cascade,
	resp_ril_persona integer references persone(id) on delete cascade on update cascade
);

create table biomassa_struttura (
	id_rilevazione integer primary key references rilevazioni(id) on delete cascade on update cascade,
	larghezza_chioma integer,
	lunghezza_chioma integer,
	peso_fresco_chioma integer,
	peso_secco_chioma integer,
	altezza_pianta integer,
	lunghezza_radice integer
);

create table alterazioni_fioritura_fruttificazione (
	id_rilevazione integer primary key  references rilevazioni(id) on delete cascade on update cascade,
	n_frutti integer,
	n_fiori integer,
	peso_fresco_radici integer,
	peso_secco_radici integer
);

create table altri_danni (
	id_rilevazione integer primary key references rilevazioni(id) on delete cascade on update cascade,
	n_foglie_danneggiate integer,
	perc_sup_danneggiata_foglia integer check (perc_sup_danneggiata_foglia between 0 and 100)
);

create table parametri_suolo (
	id_rilevazione integer primary key references rilevazioni(id) on delete cascade on update cascade,
	ph decimal(3,1),
	umidita decimal(5,2) check (umidita between 0 and 100), -- considerata come percentuale
	temperatura decimal (3,1)
);
