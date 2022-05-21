drop table cancion;
drop table album;
drop table artista;

--Creación de la tabla de Artista
create table artista(
    cod_art int constraint pk_artista primary key,
    nome varchar(30) not null unique,
    verificacion boolean not null,
    data_nacemento date,
    cidade_orixen varchar(50)
);

--Creación de la tabla Albúm
create table album(
    cod_alb int constraint pk_album primary key,
    titulo varchar(50) not null unique,
    ano_creacion int not null,
    cod_art_owner int,
    constraint fk_artist FOREIGN key(cod_art_owner) 
        references artista(cod_art)
);

--Creación de la tabla de canción
create table cancion(
    cod_song int constraint pk_song primary key,
    titulo varchar(50) not null,
    duracion int not null constraint check_duracion check (duracion > 0),
    ano_creacion int not null,
    explicito boolean not null,
    num_reproducciones bigint default 0,
    xenero varchar(20),
    cod_album int,
    cod_artist int not null,
    constraint fk_album FOREIGN key(cod_album)
        references album(cod_alb) deferrable initially deferred,
    constraint fk_artista FOREIGN key(cod_artist)
        references artista(cod_art)
);


-- Insert de Artistas
Insert into artista values(1, 'Santi', True, '14-02-2000', 'Maracaibo');
Insert into artista values(2, 'adrian', True, '14-02-2000');
Insert into artista values(3, 'mosqueira', false, null,'coruña');

--Insert de canciones
Insert into cancion values(1, 'Time', 360, 1975, false, 1000, 'Rock psicodelico', null, 1);
Insert into cancion values(2, 'Money', 360, 1973, True, null, null, null, 2);