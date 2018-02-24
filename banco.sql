create database testeInternalSistem;

create table email(
email_id			varchar(32) primary key,
data_recebimento	datetime,
origem				varchar(300),
assunto				varchar(500)
);

drop table email;

select * from email;

truncate email;