drop table interpreta;
drop table cancion;
drop table album;
drop table artista;

--Creación de la tabla de Artista
create table artista(
    cod_art int constraint pk_artista primary key,
    nome varchar(30) not null,
    verification boolean not null,
    data_nacemento date,
    cidade_orixen varchar(50)
);

--Creación de la tabla Albúm
create table album(
    cod_alb int constraint pk_album primary key,
    titulo varchar(50) not null,
    año_creacion int not null,
    cod_art_owner int,
    constraint fk_artist FOREIGN key(cod_art_owner) 
        references artista(cod_art)
);

--Creación de la tabla de canción
create table cancion(
    cod_song int constraint pk_song primary key,
    titulo varchar(50) not null,
    duracion int not null,
    año_creacion int not null,
    explicito boolean not null,
    num_reproducciones int default 0,
    genero varchar(20),
    cod_album int,
    constraint fk_album FOREIGN key(cod_album)
        references album(cod_alb)
);

--Creación de la tabla interpreta
create table interpreta(
    cod_song int,
    cod_art_owner int,
    constraint pk_interpreta Primary key(cod_song, cod_art_owner),
    constraint fk_cancion FOREIGN key(cod_song)
        references cancion(cod_song),
    constraint fk_artista FOREIGN key(cod_art_owner)
        references artista(cod_art)
);