-- tutte le persone che hanno id > 2000 (anche se non ha senso) o sono dei musicisti
select * from persone where id > 2000 or ruolo = 'Musician';

create index ruolo_persona_hash on persone using hash (ruolo);

-- tutte le repliche relative alla specie 'Clematis vitalba'
select * from repliche where nome_scientifico_specie='Clematis vitalba'

create index replica_specie_hash on repliche using hash (nome_scientifico_specie);

-- seleziona id, nome e istituto dell'orto dove sono state piantate repliche dopo una certa data ('1-4-2023 00:00:00')
select o.id, o.nome, o.istituto
from repliche r join orti o
on r.id_orto=o.id
where data_dimora > '1-4-2023 00:00:00'

create index replica_data_dimora on repliche (data_dimora);
