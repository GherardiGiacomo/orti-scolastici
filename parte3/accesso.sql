CREATE ROLE studente;
CREATE ROLE insegnante;
CREATE ROLE referente_scuola;
CREATE ROLE referente_istituto;
CREATE ROLE gestore_progetto;

GRANT studente TO insegnante;
GRANT insegnante TO referente_scuola;
GRANT referente_scuola TO referente_istituto;
GRANT referente_istituto TO gestore_progetto;

--studenti 
GRANT SELECT ON TABLE rilevazioni TO studente;
GRANT SELECT ON TABLE parametri_suolo TO studente;
GRANT SELECT ON TABLE altri_danni TO studente;
GRANT SELECT ON TABLE alterazioni_fioritura_fruttificazione TO studente;
GRANT SELECT ON TABLE biomassa_struttura TO studente;
GRANT SELECT ON TABLE associazioni_sensore TO studente;
GRANT SELECT ON TABLE sensori TO studente;
GRANT SELECT ON TABLE specie TO studente;
GRANT SELECT ON TABLE repliche TO studente;
GRANT SELECT ON TABLE gruppi_controllo TO studente;
GRANT SELECT ON TABLE gruppi TO studente;
GRANT SELECT ON TABLE orti TO studente;
GRANT INSERT ON TABLE rilevazioni TO studente;
GRANT INSERT ON TABLE parametri_suolo TO studente;
GRANT INSERT ON TABLE altri_danni TO studente;
GRANT INSERT ON TABLE alterazioni_fioritura_fruttificazione TO studente;
GRANT INSERT ON TABLE biomassa_struttura TO studente;
GRANT INSERT ON TABLE repliche TO studente;

--insegnanti 
GRANT SELECT ON TABLE classi TO insegnante;
GRANT UPDATE, DELETE ON TABLE rilevazioni TO insegnante;
GRANT UPDATE, DELETE ON TABLE parametri_suolo TO insegnante;
GRANT UPDATE, DELETE ON TABLE altri_danni TO insegnante;
GRANT UPDATE, DELETE ON TABLE alterazioni_fioritura_fruttificazione TO insegnante;
GRANT UPDATE, DELETE ON TABLE biomassa_struttura TO insegnante;
GRANT INSERT, UPDATE, DELETE ON TABLE associazioni_sensore TO insegnante;
GRANT INSERT, UPDATE, DELETE ON TABLE sensori TO insegnante;
GRANT UPDATE, DELETE ON TABLE repliche TO insegnante;
GRANT INSERT, UPDATE, DELETE ON TABLE gruppi TO insegnante;
GRANT SELECT ON TABLE riferimenti_scuole TO insegnante;
GRANT SELECT ON TABLE scuole TO insegnante;

--ref scuola  
GRANT INSERT, UPDATE, DELETE ON TABLE gruppi_controllo TO referente_scuola;
GRANT INSERT, UPDATE, DELETE ON TABLE classi TO referente_scuola;
GRANT SELECT ON TABLE riferimenti_istituto TO referente_scuola;

--ref istituto 
GRANT INSERT, UPDATE, DELETE ON TABLE orti TO referente_istituto;
GRANT INSERT ON TABLE riferimenti_scuole TO referente_istituto;
GRANT INSERT ON TABLE scuole TO referente_istituto;
GRANT SELECT, INSERT ON TABLE persone_scuola TO referente_istituto;
GRANT SELECT ON TABLE persone TO referente_istituto;
GRANT SELECT ON TABLE istituti TO  referente_istituto;

--gestore globale 
GRANT INSERT, UPDATE, DELETE ON TABLE istituti TO gestore_progetto;
GRANT INSERT, UPDATE, DELETE ON TABLE persone TO gestore_progetto;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE persone_scuola TO gestore_progetto;
GRANT UPDATE, DELETE ON TABLE scuole TO gestore_progetto;
GRANT UPDATE, DELETE ON TABLE riferimenti_scuola TO gestore_progetto;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE partecipanti_finanziamento TO gestore_progetto;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE finanziamenti TO gestore_progetto;
GRANT INSERT, UPDATE, DELETE ON TABLE riferimenti_istituto TO gestore_progetto;
GRANT INSERT, UPDATE, DELETE ON TABLE specie TO gestore_progetto;