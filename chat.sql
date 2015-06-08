/*
  MySQL 5.5 script.
*/

drop database if exists chat;

create database chat;

use chat;

-- grant permission
grant select, insert, update, delete on chat.* to 'Chat'@'localhost' identified by 'Chat';

-- Chinese character take 3 with UTF-8 encoding.
create table `users` (
    `id` integer not null auto_increment,
    `username` varchar(18) not null,
    `password` varchar(40) not null,
    `email` varchar(255) not null,
    `sex` varchar(4) not null,
    `avatar` longtext not null,
    `admin` bool not null default 0,
    `active` bool not null default 0,
    unique key `name_emial` (`username`, `email`),
    primary key (`id`)
) engine=innodb default charset=utf8;


create table `verify` (
    `id` integer not null auto_increment,
    `token` varchar(32) not null,
    `username` varchar(18) not null,
    unique key `token_idx` (`token`),
    primary key (`id`)
) engine=innodb default charset=utf8;


create table `losspw` (
    `id` integer not null auto_increment,
    `token` varchar(32) not null,
    `username` varchar(18) not null,
    unique key `token_idx` (`token`),
    primary key (`id`)
) engine=innodb default charset=utf8;
